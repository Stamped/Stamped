#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils, sys
import libs.ec2_utils

from libs.ElasticMongo import ElasticMongo

if __name__ == '__main__':
    config_ns  = 'local.elasticmongo'
    es_port    = 9200
    db_port    = 27017
    
    es_servers = []
    db_servers = []
    
    if libs.ec2_utils.is_ec2():
        stack  = libs.ec2_utils.get_stack()
        if stack is None:
            utils.log("error: unable to find stack info")
            sys.exit(1)
        
        es_servers = filter(lambda node: 'search' in node.roles, stack.nodes)
        db_servers = filter(lambda node: 'db' in node.roles, stack.nodes)
        
        es_servers = map(lambda node: "%s:%d" % (node.private_ip_address, es_port), es_servers)
        db_servers = map(lambda node: node.private_ip_address, db_servers)
        
        if len(es_servers) == 0:
            utils.log("error: no elasticsearch servers found")
            sys.exit(1)
        
        if len(db_servers) == 0:
            utils.log("error: no db servers found")
            sys.exit(1)
    else:
        es_servers = "%s:%d" % ('localhost', es_port)
        db_servers = [ 'localhost' ]
    
    db_host = db_servers[0]
    em      = ElasticMongo(mongo_host        = db_host, 
                           mongo_port        = db_port, 
                           mongo_config_ns   = config_ns, 
                           server            = es_servers)
    
    em.run()

