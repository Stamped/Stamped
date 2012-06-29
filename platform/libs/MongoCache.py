#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

"""
Defines a decorator (mongoCachedFn) that caches results in a "cache" collection in the MongoDB until they expire
according to a specified max staleness. This cache is useful because it persists on the hard drive through
reboots &c.

Note that ALL function results are cached. So if you have a function result you do not want to cache -- for instance,
a query to a third-party source that doesn't return results -- you need to throw an exception instead of just returning
an empty value, because exceptions are not caught or cached.

Add the kwarg force_recalculate=True to any call to a mongo cached fn to bypass the cache.

Execute this file (python MongoCache.py) to clean out expired items in the mongo cache, or run it with the command-line
argument "purge" to clean out the mongo cache entirely.
"""

import Globals
import binascii, bson, datetime, ec2_utils, functools, logs, utils, pylibmc
from pymongo.errors import AutoReconnect
from api.db.mongodb.AMongoCollection import MongoDBConfig
from schema import Schema


#####################################################################
########################### SERIALIZATION ###########################
#####################################################################

# Huge TODO: There's no good reason to serialize all of this shit and then hash it.
# I should just hash it in the first place, with some care taken to avoid the problem
# of class objects that are hashable but really shouldn't be.

class SerializationError(Exception):
    def __init__(self, string):
        super(SerializationError, self).__init__(string)

basic_types = [basestring, int, float, bool]

def isBasicType(x):
    return x is None or any(isinstance(x, basic_type) for basic_type in basic_types)

def argIsSerializable(original_arg):
    queue = [original_arg]
    while queue:
        arg = queue.pop()

        if isBasicType(arg):
            continue
        elif isinstance(arg, list) or isinstance(arg, set) or isinstance(arg, tuple):
            queue.extend(arg)
        elif isinstance(arg, dict):
            queue.extend(arg.keys())
            queue.extend(arg.values())
        else:
            print "Can't handle type", type(arg)
            return False
    return True


def assertCallIsSerializable(args, kwargs):
    for idx, arg in enumerate(args):
        if not argIsSerializable(arg):
            raise SerializationError('Failed to serialize %dth argument value: (%s)' % (idx, str(arg)))

    for key, val in kwargs.items():
        if not argIsSerializable(val):
            raise SerializationError('Failed to serialize "%s" keyword argument value: (%s)' % (key, str(val)))


def serializeArgument(arg):
    """
    Yeah the name is a misnomer at this point. Just converts it into all immutable hashable types.
    """
    if isBasicType(arg):
        return arg
    elif isinstance(arg, list) or isinstance(arg, set) or isinstance(arg, tuple):
        return tuple(map(serializeArgument, arg))
    elif isinstance(arg, dict):
        # Technically this means you can have collisions -- for instance, the call foo({1: 2, 4: 3})
        # would collide with the call foo([(1, 2), (4, 3)]) -- but whatever.
        return tuple((serializeArgument(key), serializeArgument(value)) for key, value in arg.items())
    # We don't expect to get here; assertCallIsSerializable should have found the problem first.
    raise SerializationError('Unexpectedly failed to serialize arg: (%s)' % str(arg))


def serializeValue(arg, schemaClasses):
    """
    Takes types Mongo can't handle and converts them into types it can.
    """
    def recurse(arg2):
        return serializeValue(arg2, schemaClasses)

    if isBasicType(arg):
        return arg
    elif isinstance(arg, list) or isinstance(arg, set) or isinstance(arg, tuple):
        return [arg.__class__.__name__] + map(recurse, arg)
    elif isinstance(arg, dict):
        if not arg:
            return {}
        keys, values = zip(*arg.items())
        if not all(isinstance(key, basestring) for key in keys):
            raise SerializationError('All dict keys must be strings in serialized values for MongoCache!')
        return dict(zip(map(recurse, keys), map(recurse, values)))
    elif isinstance(arg, Schema):
        className = arg.__class__.__name__
        if className not in schemaClasses:
            raise SerializationError('Unable to serialize schema of type %s without class being passed to decorator!' %
                                     className)
        return { '__schema_class__': className,
                 '__data__': arg.dataExport() }

def deserializeValue(arg, schemaClasses):
    def recurse(arg2):
        return deserializeValue(arg2, schemaClasses)

    if isBasicType(arg):
        return arg
    elif isinstance(arg, list):
        # Tuples, sets, and lists all end up as lists, so the first element of the serialized list tell us what type it
        # was originally.
        containerType = eval(arg[0])
        return containerType(map(recurse, arg[1:]))
    elif isinstance(arg, dict):
        # Schemas and dicts both end up as dicts so we use the presence/absence of __schema_class__ to differentiate.
        schemaClassName = arg.pop('__schema_class__', None)
        if schemaClassName:
            schemaClass = schemaClasses[schemaClassName]
            return schemaClass().dataImport(arg['__data__'])
        else:
            keys, values = zip(*arg.items())
            # Keys must be strings, so we don't have to bother deserializing.
            return dict(zip(keys, map(recurse, values)))



#####################################################################
############################# DECORATOR #############################
#####################################################################

def hashFunctionCall(fnName, args, kwargs):
    """Serialize the arguments to the function call into a concise cache key.

    In this case we convert sets, lists and dicts to tuples (only going one level deep) and try to hash. This will
    fail if there are nested lists/dicts or if there are class objects."""

    args = tuple(map(serializeArgument, args))
    # TODO: This relies on the fact that keys() and values() are always in the same order. Is this safe?
    if not kwargs:
        kwargs = ()
    else:
        keys, values = zip(*kwargs.items())
        kwargs = tuple(zip(map(serializeArgument, keys), map(serializeArgument, values)))

    return hash((fnName, args, kwargs))


# Globals. Ugh.
# This one is used to remember whether or not we've had any problems connecting to the mongod instance, so that if we
# have we won't keep trying each time. (There's a long timeout per attempt.)
cacheTableError = None
# This one is used for testing so we know not to use timestamps when we're running in testing mode.
disableStaleness = False
# This one is used for testing also. For tests, we throw a CacheMissException on cache misses. This is to make sure that
# (a) the test runs the same whether or not you have an internet connection and (b) that if a third-party call failed
# in the first run it fails in the second, though not necessarily with the same error.
exceptionOnCacheMiss = False

class CacheMissException(Exception):
    def __init__(self, functionName):
        super(CacheMissException, self).__init__('Got cache miss for call to MongoCached function: ' + functionName)

ONE_WEEK = datetime.timedelta(7)
def mongoCachedFn(maxStaleness=ONE_WEEK, memberFn=True, schemaClasses=[]):
    # Don't use Mongo caching in production.
    assert(not utils.is_ec2())

    schemaClassesMap = {}
    for schemaClass in schemaClasses:
        schemaClassesMap[schemaClass.__name__] = schemaClass

    def decoratingFn(userFunction):
        userFnName = userFunction.func_name

        @functools.wraps(userFunction)
        def wrappedFn(*args, **kwargs):
            global cacheTableError
            if cacheTableError is not None:
                # We haven't been able to connect to the cache. MongoDB may not be running. Just issue the call.
                return userFunction(*args, **kwargs)

            now = datetime.datetime.now()
            fullArgs = args

            if memberFn == True:
                self = args[0]
                fnName = '%s.%s' % (self.__class__.__name__, userFnName)
                args = args[1:]
            else:
                fnName = userFnName

            assertCallIsSerializable(args, kwargs)
            callHash = hashFunctionCall(fnName, args, kwargs)

            force_recalculate = kwargs.pop('force_recalculate', False)
            try:
                connection = MongoDBConfig.getInstance().connection
                dbname = MongoDBConfig.getInstance().database_name
                table = getattr(connection, dbname).cache
                result = table.find_one({'_id':callHash})
            except AutoReconnect as exc:
                cacheTableError = exc
                logs.warning("Couldn't connect to Mongo cache table; disabling Mongo cache.")
                return userFunction(*fullArgs, **kwargs)

            if result is None and exceptionOnCacheMiss:
                raise CacheMissException(fnName)
            if result and result['expiration'] is None and not disableStaleness:
                raise ValueError('We should never be using non-expiring cache entries outside of test fixtures!')
            if result and result['expiration'] is not None and disableStaleness:
                raise ValueError('We should never be using expiring cache entries inside of test fixtures!')

            if result and (disableStaleness or (result['expiration'] > now)) and not force_recalculate:
                # We hit the cache and the result isn't stale! Woo!
                return deserializeValue(result['value'], schemaClassesMap)

            expiration = None if disableStaleness else now + maxStaleness
            result = userFunction(*fullArgs, **kwargs)
            cacheEntry = {'_id':callHash,
                          'func_name': fnName,
                          'value': serializeValue(result, schemaClassesMap),
                          'expiration':expiration}
            table.update({'_id':callHash}, cacheEntry, upsert=True)
            return result

        return wrappedFn

    return decoratingFn


import sys

if __name__ == '__main__':
    connection = MongoDBConfig.getInstance().connection
    table = connection.stamped.cache
    if len(sys.argv) > 1 and sys.argv[1] == 'purge':
        table.drop()
    else:
        table.remove({'expiration':{'$lt':datetime.datetime.now()}})