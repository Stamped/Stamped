#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils, sys
import libs.ec2_utils

from libs.ElasticMongo      import ElasticMongo
from api.MongoStampedAPI    import MongoStampedAPI

"""
import pyes
es   = pyes.ES('10.85.105.209:9200')
info = es.collect_info()
from pprint import pprint; pprint(info)
"""

if __name__ == '__main__':
    config_ns  = 'local.elasticmongo'
    es_port    = 9200
    db_port    = 27017
    
    if libs.ec2_utils.is_ec2():
        stack  = libs.ec2_utils.get_stack()
        if stack is None:
            utils.log("error: unable to find stack info")
            sys.exit(1)
        
        es_servers = filter(lambda node: 'search' in node.roles, stack.nodes)
        es_servers = map(lambda node: str("%s:%d" % (node.private_ip_address, es_port)), es_servers)
        
        if len(es_servers) == 0:
            utils.log("error: no elasticsearch servers found")
            sys.exit(1)
        
        api  = MongoStampedAPI(lite_mode=True)
        conn = api._entityDB._collection._connection
        em   = ElasticMongo(mongo_conn          = conn, 
                            mongo_config_ns     = config_ns, 
                            server              = es_servers, 
                            dump_curl           = '/stamped/logs/elasticsearch_es.log')
    else:
        em   = ElasticMongo(mongo_host          = 'localhost', 
                            mongo_port          = db_port, 
                            mongo_config_ns     = config_ns, 
                            server              = "%s:%d" % ('localhost', es_port))
    
    em.run()

