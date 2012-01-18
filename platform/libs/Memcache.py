#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import binascii, bson, ec2_utils, functools, logs, utils, pylibmc

from schema import Schema

# TODO: Manipulating cache items via subscript-style syntax (e.g., cache[key]) 
# is currently the only way pickling import/export conversion will take place 
# for Schema objects. Depending on our needs in the future, we may need expand 
# support for these conversions to the entire pylibmc.Client interface.

class Memcache(object):
    """
        Lightweight wrapper around pylibmc memcached client which handles client 
        initialization by obtaining the list of memcached servers from EC2 tags.
        Also handles importing / exporting from / to our ORM, Schema, and 
        pylibmc's basic, pickleable data types.
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
        except Exception, e:
            logs.error("[%s] unable to initialize memcached (%s)" % (self, e))
            self._client = None
            return False
        
        return True
    
    def __getattr__(self, key):
        # proxy any attribute lookups to the underlying pylibmc client
        if self._client:
            return self._client.__getattribute__(key)
    
    def __setitem__(self, key, value):
        if self._client:
            self._client[key] = self._import_value(value)
    
    def __getitem__(self, key):
        if self._client:
            return self._export_value(self._client[key])
        
        raise KeyError(key)
    
    def __contains__(self, key):
        if self._client:
            return key in self._client
        
        return False
    
    def _import_value(self, value):
        """
            returns a custom, pickleable version of the given value for storage 
            within memcached.
        """
        
        if isinstance(value, Schema):
            return {
                "__schema__" : value.__class__, 
                "__value__"  : value.value, 
            }
        elif isinstance(value, (list, tuple)):
            value = map(self._import_value, value)
        
        return value
    
    def _export_value(self, value):
        """
            converts the custom, pickleable version of the given value stored 
            within memcached into our own, pythonic version that is returned.
        """
        
        if isinstance(value, dict) and '__schema__' in value and '__value__' in value:
            # reinstantiate the Schema subclass with its prior data
            return value['__schema__'](value['__value__'])
        elif isinstance(value, (list, tuple)):
            value = map(self._export_value, value)
        
        return value
    
    def __str__(self):
        if self._client:
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

class InvalidatingMemcache(Memcache):
    
    def _import_object_id(object_id):
        return bson.objectid.ObjectId(object_id).binary
    
    def _export_object_id(binary_object_id):
        return binascii.hexlify(binary_object_id)
    
    def _import_value(self, value):
        dependencies = self._find_dependencies(values)
        # TODO: store dependencies
        
        return super(InvalidatingMemcache, self)._import_value(value)
    
    def _get_object_id(self, value):
        if isinstance(value, basestring) and 24 == len(value):
            try:
                return self._import_object_id(value)
            except:
                pass
        
        return None
    
    def _find_dependencies(self, value):
        _get_object_id = self._get_object_id
        dependencies   = []
        
        try:
            for v in value:
                object_id = _get_object_id(v)
                
                if object_id is not None:
                    dependencies.append(object_id)
                else:
                    dependencies.extend(self._find_dependencies(v))
        except TypeError:
            object_id = _get_object_id(value)
            
            if object_id is not None:
                dependencies.append(object_id)
        except:
            pass
        
        return dependencies

def memcached_function(get_cache_client, time=0, min_compress_len=0):
    
    def decorating_function(user_function):
        kwd_mark   = object() # separate positional and keyword args
        key_prefix = user_function.func_name
        
        @functools.wraps(user_function)
        def wrapper(*args, **kwds):
            # note: treat args[0] specially (self)
            args2 = args[1:]
            cache = getattr(args[0], get_cache_client)()
            
            # cache key records both positional and keyword args
            key = "%s:%s" % (key_prefix, args2)
            
            if kwds:
                key += (kwd_mark,) + tuple(sorted(kwds.items()))
            
            # get cache entry or compute if not found
            store   = False
            compute = True
            
            try:
                result = cache[key]
                wrapper.hits += 1
                compute = False
            except KeyError:
                store = True
            except:
                store = False
            
            if compute:
                result = user_function(*args, **kwds)
                wrapper.misses += 1
            
            if store:
                cache_set = cache.set
                if cache_set is not None:
                    cache_set(key, result, time=time, min_compress_len=min_compress_len)
            
            return result
        
        def clear():
            cache_flush_all = cache.flush_all
            if cache_flush_all is not None:
                cache_flush_all()
            
            wrapper.hits = wrapper.misses = 0
        
        wrapper.hits  = wrapper.misses = 0
        wrapper.clear = clear
        return wrapper
    
    return decorating_function

