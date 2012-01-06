#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__   = "TODO"

import os, ec2_utils, pylibmc

class Memcache(object):
    """
        Lightweight wrapper around pylibmc memcached client which handles client 
        initialization by obtaining the list of memcached servers from EC2 tags.
    """
    
    def __init__(self, binary=False, behaviors=None):
        self.init(binary, behaviors)
    
    def init(self, binary=False, behaviors=None):
        memcached_nodes = []
        
        if is_ec2():
            stack = ec2_utils.get_stack()
            
            for node in stack.nodes:
                if 'mem' in node.roles:
                    memcached_nodes.append(node.private_ip_address)
            
            if 0 == len(memcached_nodes):
                print "[%s] unable to any find memcached servers" % self
                return False
        else:
            # running locally so default to localhost
            memcached_nodes.append('127.0.0.1')
        
        self._client = pylibmc.Client(memcached_nodes)
        #, binary, behaviors)
        
        return True
    
    def __getattr__(self, key):
        try:
            return object.__getattr__(self, key)
        except:
            return eval("self._client.%s" % key)
    
    def __setitem__(self, name, value):
        self._client[name] = value
    
    def __getitem__(self, name):
        return self._client[name]
    
    def __str__(self):
        return self.__class__.__name__

class StampedMemcache(Memcache):
    
    def __init__(self):
        # TODO: revisit the default behavior options
        Memcache.__init__(self, binary=True, behaviors={
            'remove_failed' : 5, 
            'no_block'      : True, 
            'ketama'        : True, 
        })

def is_ec2():
    """ returns whether or not this python program is running on EC2 """
    
    return os.path.exists("/proc/xen") and os.path.exists("/etc/ec2_version")


