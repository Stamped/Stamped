#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import math, time

from api.MongoStampedAPI import MongoStampedAPI

def __get_collection(db, ns):
    collection = db
    
    for component in ns.split('.'):
        collection = collection[component]
    
    return collection

def safe_insert(coll, documents, retries = 5, delay = 0.25):
    """
        Retry wrapper around a single mongo bulk insertion.
    """
    
    while True:
        try:
            return coll.insert(documents)
        except AutoReconnect as e:
            retries -= 1
            
            if retries <= 0:
                raise
            
            time.sleep(delay)
            delay *= 2

def export_config(coll, ns, drop = True):
    """
        Exports ElasticMongo mapping and index metadata to configure ElasticSearch.
    """
    
    indices  = [
        {
            'name' : 'users', 
        }, 
    ]
    
    mappings = [
        {
            'ns'        : ns, 
            'type'      : 'user', 
            'indices'   : [ 'users', ], 
            'mapping'   : {
                'name' : {
                    'boost' : 1.0, 
                    'index' : 'analyzed', 
                    'type'  : 'string', 
                    'term_vector' : 'with_position_offsets', 
                }, 
                'screen_name' : {
                    'boost' : 2.0, 
                    'index' : 'analyzed', 
                    'type'  : 'string', 
                    'term_vector' : 'with_position_offsets', 
                }, 
                'stats' : {
                    'num_stamps' : {
                        'index'         : 'not_analyzed', 
                        'store'         : 'yes', 
                        'type'          : 'integer', 
                        'null_value'    : 0, 
                    }, 
                    'num_followers' : {
                        'index'         : 'not_analyzed', 
                        'store'         : 'yes', 
                        'type'          : 'integer', 
                        'null_value'    : 0, 
                    }, 
                }, 
            }, 
        }, 
    ]
    
    if drop:
        coll.indices.drop()
        coll.mappings.drop()
        coll.state.drop()
    
    m = "indices"  if len(indices)  != 1 else "index"
    i = "mappings" if len(mappings) != 1 else "mapping"
    
    utils.log("exporting %d %s and %d %s" % (len(indices), i, len(mappings), m))
    safe_insert(coll.indices,  indices)
    safe_insert(coll.mappings, mappings)

def export():
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-D', '--drop', action="store_true", default=False,
                        help="drop existing collections before performing any insertions")
    parser.add_argument("-d", "--db", default=None, type=str, help="db to connect to")
    parser.add_argument('-o', '--output_namespace', type=str, default="stamped.users",
                        help=("mongo db and collection namespace to store output to "
                              "in dot-notation (e.g., defaults to stamped.users)"))
    parser.add_argument('-s', '--state_namespace', type=str, default="local.elasticmongo", 
                        help=("mongo db and collection namespace to store elasticmongo "
                              "mapping and index metadata"))
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    
    args = parser.parse_args()
    
    if args.db:
        utils.init_db_config(args.db)
    
    api  = MongoStampedAPI(lite_mode=True)
    conn = api._entityDB._collection._connection
    coll = __get_collection(conn, args.state_namespace)
    
    export_config(coll, args.output_namespace, args.drop)

if __name__ == '__main__':
    export()

