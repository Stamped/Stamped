#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import time, utils
import pysolr, pymongo

from collections    import defaultdict
from pprint         import pprint

def solr_id(id):
    if isinstance(id, basestring) or isinstance(id, int):
        return id
    else:
        return repr(id)

def extract_fields(obj, fields):
    doc = {'id': solr_id(obj['_id'])}
    
    for field in obj.keys():
        if field in fields:
            doc[field] = obj[field]
    
    return doc

def init(conn, solr, schemas):
    for ns, fields in schemas.items():
        print("Importing all documents from ns '%s' to solr" % ns)
        
        coll = conn
        for part in ns.split('.'):
            coll = coll[part]
        
        print str([extract_fields(obj, fields) for obj in coll.find()])
        #solr.add([extract_fields(obj, fields) for obj in coll.find()])

def run(mongo_host='localhost', mongo_port=27017, solr_url="http://127.0.0.1:8983/solr/"):
    conn = pymongo.Connection(mongo_host, mongo_port)
    db   = conn.local
    #solr = pysolr.Solr(solr_url)
    solr = None
    
    schemas = defaultdict(set)
    for o in db.fts.schemas.find():
        schemas[o['ns']] = schemas[o['ns']].union(o['fields'])
    
    cursor = None
    spec   = {}
    
    state = db.fts.find_one({'_id': 'state'})
    if state and 'ts' in state:
        first = db.oplog['$main'].find_one()
        if (first['ts'].time > state['ts'].time and
            first['ts'].inc > state['ts'].inc):
            
            init(conn, solr, schemas)
        else:
            spec['ts'] = {'$gt': state['ts']}
    else:
        init(conn, solr, schemas)
    
    while True:
        if not cursor or not cursor.alive:
            cursor = db.oplog.rs.find(spec, tailable=True).sort("$natural", 1)
        
        solr_docs = []
        for op in cursor:
            pprint(op)
            
            if op['ns'] in schemas:
                spec['ts'] = {'$gt': op['ts']}
                
                if op['op'] == 'd':
                    id = solr_id(op['o']['_id'])
                    print("Deleting document with id '%s'" % id)
                    #solr.delete(id=id)
                elif op['op'] in ['i', 'u']:
                    solr_docs.append(extract_fields(op['o'], schemas[op['ns']]))
        
        if solr_docs:
            print('Adding %d docs to solr' % len(solr_docs))
            #solr.add(solr_docs)
        
        db.fts.save({'_id': 'state', 'ts': spec['ts']['$gt']})
        time.sleep(1)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--mongo_host', '-m', dest='mongo_host', type=str, default="localhost",
                        help=("hostname or IP address of the Mongo instance to use"))
    parser.add_argument('--mongo_port', '-p', dest='mongo_port', type=int, default=27017,
                        help="port number of the Mongo instance")
    parser.add_argument('--solr_url', '-s', dest='solr_url', type=str, default="http://127.0.0.1:8983/solr/",
                        help="URL of the Solr instance to use")
    parser.add_argument('--version', '-v', action='version', version='%(prog)s ' + __version__)
    
    args = parser.parse_args()
    
    run(mongo_host=args.mongo_host, mongo_port=args.mongo_port, solr_url=args.solr_url)

