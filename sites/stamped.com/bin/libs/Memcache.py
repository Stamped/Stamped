#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils, ec2_utils, pylibmc
from schemas import Schema

# TODO: Manipulating cache items via subscript-style syntax (e.g., cache[key]) 
# is currently the only way pickling import/export conversion will take place 
# for Schema objects. Depending on our needs in the future, we may need expand 
# support for these conversions to the entire pylibmc.Client interface.

class Memcache(object):
    """
        Lightweight wrapper around pylibmc memcached client which handles client 
        initialization by obtaining the list of memcached servers from EC2 tags.
    """
    
    def __init__(self, binary=False, behaviors=None):
        self.init(binary, behaviors)
    
    def init(self, binary=False, behaviors=None):
        memcached_nodes = []
        
        if utils.is_ec2():
            stack = ec2_utils.get_stack()
            
            for node in stack.nodes:
                if 'mem' in node.roles:
                    memcached_nodes.append(node.private_ip_address)
            
            if 0 == len(memcached_nodes):
                utils.log("[%s] unable to any find memcached servers" % self)
                return False
        else:
            # running locally so default to localhost
            memcached_nodes.append('127.0.0.1')
        
        self._client = pylibmc.Client(memcached_nodes, binary=binary, behaviors=behaviors)
        return True
    
    def __getattr__(self, key):
        # proxy any attribute lookups to the underlying pylibmc client
        return self._client.__getattribute__(key)
    
    def __setitem__(self, key, value):
        self._client[key] = self._import_value(value)
    
    def __getitem__(self, key):
        return self._export_value(self._client[key])
    
    def __contains__(self, key):
        return key in self._client
    
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
        
        return value
    
    def _export_value(self, value):
        """
            converts the custom, pickleable version of the given value stored 
            within memcached into our own, pythonic version that is returned.
        """
        
        if isinstance(value, dict) and '__schema__' in value and '__value__' in value:
            # reinstantiate the Schema subclass with its prior data
            return value['__schema__'](value['__value__'])
        
        return value
    
    def __str__(self):
        return "%s(%s)" % (str(self._client), self.__class__.__name__)

class StampedMemcache(Memcache):
    
    def __init__(self):
        # TODO: revisit these behavior options
        Memcache.__init__(self, binary=True, behaviors={
            'remove_failed' : 5, 
            'no_block'      : True, 
            'ketama'        : True, 
        })

