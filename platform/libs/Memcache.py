#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import binascii, bson, ec2_utils, functools, logs, utils, pylibmc, json, datetime

from schema import Schema

"""
NOTE (travis): Manipulating cache items via subscript-style syntax (e.g., cache[key]) 
is currently the only way pickling import/export conversion will take place for 
Schema objects. Depending on our needs in the future, we may need expand support 
for these conversions to the entire pylibmc.Client interface.
"""

class Memcache(object):
    """
        Lightweight wrapper around the pylibmc memcached client which handles 
        client initialization by obtaining the list of memcached servers from 
        EC2 tags. Also handles importing / exporting from / to our ORM, Schema, 
        and pylibmc's basic, pickleable data types.
    """
    
    def __init__(self, binary=False, behaviors=None):
        self._client = None
        self.init(binary, behaviors)
    
    def init(self, binary=False, behaviors=None):
        try:
            memcached_nodes = []
            
            if utils.is_ec2():
                stack = ec2_utils.get_stack()
                
                for node in stack.nodes:
                    if 'mem' in node.roles:
                        memcached_nodes.append(node.private_ip_address)
                
                if 0 == len(memcached_nodes):
                    raise Exception("[%s] unable to any find memcached servers" % self)
            else:
                # running locally so default to localhost
                memcached_nodes.append('127.0.0.1')
            
            self._client = pylibmc.Client(memcached_nodes, binary=binary, behaviors=behaviors)
            
            # Verify it works
            self._client.set('test', 'test', time=0)

        except Exception, e:
            logs.warning("[%s] unable to initialize memcached (%s)" % (self, e))
            self._client = None
            return False

        return True

    def flush_all(self):
        if self._client:
            self._client.flush_all()
    
    def set(self, key, value, *args, **kwargs):
        if self._client is not None:
            try:
                self._client.set(key, value, *args, **kwargs)
            except Exception, e:
                logs.warn(str(e))
    
    def __getattr__(self, key):
        # proxy any attribute lookups to the underlying pylibmc client
        if self._client is not None:
            return self._client.__getattribute__(key)
    
    def __setitem__(self, key, value):
        if self._client is not None:
            self._client[key] = value
    
    def __getitem__(self, key):
        if self._client is not None:
            try:
                return self._client[key]
            except Exception:
                pass
        
        raise KeyError(key)

    def __delitem__(self, key):
        if self._client is not None:
            try:
                del(self._client[key])
            except Exception:
                pass
    
    def __contains__(self, key):
        if self._client is not None:
            return key in self._client
        
        return False
    
    def __str__(self):
        if self._client is not None:
            return "%s(%s)" % (str(self._client), self.__class__.__name__)
        else:
            return "%s" % self.__class__.__name__

class StampedMemcache(Memcache):
    
    def __init__(self):
        # TODO: revisit these options
        Memcache.__init__(self, binary=True)
        """, behaviors={
            'remove_failed' : 5, 
            'no_block'      : True, 
            'ketama'        : True, 
        })
        """

# what keys are we using for memcached entries?
# object_id => [ dependencies ]


__globalMemcache = None

def globalMemcache():
    global __globalMemcache

    if __globalMemcache is None:
        __globalMemcache = StampedMemcache()

    return __globalMemcache


def generateKeyFromDictionary(dictionary):
    dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else obj
    return json.dumps(dictionary, sort_keys=True, separators=(',',':'), default=dthandler)


def memcached_function(time=0, min_compress_len=0):
    
    def decorating_function(user_function):

        key_prefix = user_function.func_name

        @functools.wraps(user_function)
        def wrapper(*args, **kwargs):
            # note: treat args[0] specially (self)
            self  = args[0].__class__.__name__
            args2 = args[1:]
            cache = globalMemcache()
            mark  = ';'
            
            # Cache key records both positional and keyword args
            key   = "wrapper::%s::%s(" % (self, key_prefix)
            
            def encode_arg(arg):
                if isinstance(arg, Schema):
                    # Convert to JSON to efficiently convert to string / sort by keys
                    return generateKeyFromDictionary(arg.dataExport())
                else:
                    # Convert any unicode characters to string representation
                    return unicode(arg).encode('utf8')

            if len(args) > 0:
                key += mark.join(map(encode_arg, args2))
            
            if kwargs:
                suffix = mark.join(('%s=%s' % (k, encode_arg(v)) for k, v in sorted(kwargs.items())))
                
                if len(args2) > 0 and not key.endswith(mark):
                    key += "%s%s" % (mark, suffix)
                else:
                    key += suffix
            
            key += ')'

            logs.debug("Memcached Key: %s" % key)
            
            # get cache entry or compute if not found
            store   = False
            compute = True
            
            try:
                result  = cache[key]
                compute = False
                
                wrapper.hits += 1
                logs.debug("Memcached Hit")
            except KeyError:
                store = True
            except Exception:
                store = False
            
            if compute:
                result = user_function(*args, **kwargs)
                wrapper.misses += 1
            
            if store:
                cache_set = cache.set
                
                if cache_set is not None:
                    try:
                        logs.debug("Store in Memcached")
                        cache_set(key, result, time=time, min_compress_len=min_compress_len)
                    except Exception, e:
                        logs.warning(str(e))
            
            return result
        
        def clear():
            cache_flush_all = cache.flush_all
            if cache_flush_all is not None:
                cache_flush_all()
            
            wrapper.hits = wrapper.misses = 0
        
        wrapper.hits  = wrapper.misses = 0
        wrapper.clear = clear
        
        return wrapper
        """
        # Temporary replacement to nullify actions
        @functools.wraps(user_function)
        def wrapper(*args, **kwargs):
            return user_function(*args, **kwargs)

        return wrapper
        """
    
    return decorating_function

# note: these decorators add tiered caching to this function, such that 
# results will be cached locally with a very small LRU cache of 64 items 
# and also cached remotely via memcached with a TTL of 7 days
#@lru_cache(maxsize=64)
#@memcached_function(time=7*24*60*60)

