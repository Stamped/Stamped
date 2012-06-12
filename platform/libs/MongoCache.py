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


#####################################################################
########################### SERIALIZATION ###########################
#####################################################################

class SerializationError(Exception):
    def __init__(self, string):
        super(SerializationError, self).__init__(string)

basic_types = [basestring, int, float, bool]

def isBasicType(term):
    return any(isinstance(term, basic_type) for basic_type in basic_types)

def termIsSerializable(term, n=1):
    if isBasicType(term):
        return True

    if n == 0:
        # We're not going any deeper; at this point it needs to be all basic types.
        return False

    if isinstance(term, list) or isinstance(term, set) or isinstance(term, tuple):
        return all(termIsSerializable(inner_term, n-1) for inner_term in term)

    if isinstance(term, dict):
        return (all(termIsSerializable(inner_term, n-1) for inner_term in term.keys()) and
                all(termIsSerializable(inner_term, n-1) for inner_term in term.values()))


def assertCallIsSerializable(args, kwargs):
    for idx, arg in enumerate(args):
        if not termIsSerializable(arg):
            raise SerializationError('Failed to serialize %dth argument value: (%s)' % (idx, str(arg)))

    for key, val in kwargs.items():
        if not termIsSerializable(val):
            raise SerializationError('Failed to serialize "%s" keyword argument value: (%s)' % (key, str(val)))


def serializeTerm(term):
    if isBasicType(term) or isinstance(term, tuple):
        return term
    elif isinstance(term, list) or isinstance(term, set):
        return tuple(term)
    elif isinstance(term, dict):
        # Technically this means you can have collisions -- for instance, the call foo({1: 2, 4: 3})
        # would collide with the call foo([(1, 2), (4, 3)]) -- but whatever.
        return tuple(term.items())
    # We don't expect to get here; assertCallIsSerializable should have found the problem first.
    raise SerializationError('Unexpectedly failed to serialize term: (%s)' % str(term))

#####################################################################
############################# DECORATOR #############################
#####################################################################

def serializeCall(fnName, args, kwargs):
    """Serialize the arguments to the function call into a concise cache key.

    In this case we convert sets, lists and dicts to tuples (only going one level deep) and try to hash. This will
    fail if there are nested lists/dicts or if there are class objects."""

    args = tuple(map(serializeTerm, args))
    # TODO: This relies on the fact that keys() and values() are always in the same order. Is this safe?
    if not kwargs:
        kwargs = ()
    else:
        keys, values = zip(*kwargs.items())
        kwargs = tuple(zip(map(serializeTerm, keys), map(serializeTerm, values)))
    return hash((fnName, args, kwargs))


# Globals. Ugh.
# This one is used to remember whether or not we've had any problems connecting to the mongod instance, so that if we
# have we won't keep trying each time. (There's a long timeout per attempt.)
cacheTableError = None
# This one is used for testing so we know not to use timestamps when we're running in testing mode.
disableStaleness = False


ONE_WEEK = datetime.timedelta(7)
def mongoCachedFn(maxStaleness=ONE_WEEK, memberFn=True):
    # Don't use Mongo caching in production.
    assert(not utils.is_ec2())

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
            callHash = serializeCall(fnName, args, kwargs)

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

            if result and result['expiration'] is None and not disableStaleness:
                raise ValueError('We should never be using non-expiring cache entries outside of test fixtures!')
            if result and result['expiration'] is not None and disableStaleness:
                raise ValueError('We should never be using expiring cache entries inside of test fixtures!')

            if result and (disableStaleness or (result['expiration'] > now)) and not force_recalculate:
                # We hit the cache and the result isn't stale! Woo!
                return result['value']

            expiration = None if disableStaleness else now + maxStaleness
            result = {'_id':callHash,
                      'func_name': fnName,
                      'value': userFunction(*fullArgs, **kwargs),
                      'expiration':expiration}
            table.update({'_id':callHash}, result, upsert=True)

            return result['value']

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