#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from libs.ElasticMongo   import AElasticMongo
from libs.ElasticSearch  import ElasticSearch

class StampedElasticMongo(AElasticMongo):
    
    # MongoDB namespaces to monitor
    MONGO_NAMESPACES = {
        'stamped.users'   : {
            'indices' : 'users', 
            'type'    : 'user', 
        }, 
        'stamped.entities': {
            'indices' : 'entities', 
            'type'    : 'entity', 
        }, 
        'stamped.menus'   : {
            'indices' : 'entities', 
            'type'    : 'entity', 
        }, 
        'stamped.stamps'  : {
            'indices' : 'entities', 
            'type'    : 'entity', 
        }, 
    }
    
    def __init__(self, **kwargs):
        es = ElasticSearch(server=self._get_servers())
        
        AElasticMongo.__init__(self, es, self.MONGO_NAMESPACES.keys(), **kwargs)
    
    def _get_servers(self):
        servers = [ ]
        port = 9200
        
        if utils.is_ec2():
            stack = ec2_utils.get_stack()
            
            for node in stack.nodes:
                if 'search' in node.roles:
                    servers.append("%s:%d" % (node.private_ip_address, port))
            
            if 0 == len(servers):
                raise Exception("[%s] unable to any find search servers" % self)
        else:
            # running locally so default to localhost
            servers.append("localhost:%d" % port)
        
        return servers
    
    def add(self, ns, documents, count = None, noop = False):
        super(StampedElasticMongo, self).add(ns, documents, count, noop)
    
    def remove(self, ns, id):
        super(StampedElasticMongo, self).remove(ns, id)
    
    def _get_indices_and_type(self, ns):
        try:
            return self.MONGO_NAMESPACES[ns]
        except KeyError:
            raise Exception("[%s] received invalid namespace '%s'" % (self, ns))
    
    def _convert(self, ns, document):
        if ns not in self.MONGO_NAMESPACES:
            raise Exception("[%s] received invalid namespace '%s' for doc %s" % (self, ns, document))
        
        if ns == 'stamped.users':
            return self._convert_user(document)
        elif ns == 'stamped.entities':
            return self._convert_entity(document)
        elif ns == 'stamped.menus':
            return self._convert_menu(document)
        elif ns == 'stamped.stamps':
            return self._convert_stamp(document)
        else:
            raise Exception("[%s] LOGIC ERROR: received invalid namespace '%s' for doc %s" % (self, ns, document))
    
    def _convert_user(self, doc):
        # TODO
        raise NotImplementedError
        return doc
    
    def _convert_entity(self, doc):
        # TODO
        raise NotImplementedError
        return doc
    
    def _convert_menu(self, doc):
        # TODO
        raise NotImplementedError
        return doc
    
    def _convert_stamp(self, doc):
        # TODO
        raise NotImplementedError
        return doc

