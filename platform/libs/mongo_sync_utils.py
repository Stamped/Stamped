#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import time, utils
import argparse, pymongo

from pymongo.errors import AutoReconnect
from collections    import defaultdict
from pprint         import pprint


components:
    * poll mongo for changes in ns
    * list of indices
    * list of mappings


"""
{
    'title': {
        'boost': 1.0, 
        'index': 'analyzed', 
        'store': 'yes', 
        'type': u'string', 
        "term_vector" : "with_positions_offsets", 
    },
    'cuisine': {
        'boost': 1.0, 
        'index': 'analyzed', 
        'store': 'yes', 
        "type": u'string', 
        "term_vector" : "with_positions_offsets", 
    },
}
"""

class AMongoNotificationHandler(object):
    
    def add(self, namespace, documents):
        pass
    
    def delete(self, namespace, id):
        pass

class MongoNotificationHandler(AMongoNotificationHandler):
    
    def add(self, namespace, documents):
        print("Adding %d docs from ns '%s'" % (len(documents), namespace))
    
    def delete(self, namespace, id):
        print("Deleting document with id '%s' from ns '%s'" % (id, namespace))

def __extract_id(id):
    if isinstance(id, basestring) or isinstance(id, int):
        return id
    else:
        return repr(id)

def __extract_fields(obj, fields):
    doc = { 'id': __extract_id(obj['_id']) }
    
    for field in obj.keys():
        if field in fields:
            doc[field] = obj[field]
    
    return doc

def __init(conn, mongo_notification_handler, schemas):
    for ns, fields in schemas.items():
        print("Importing all documents from ns '%s'" % ns)
        
        coll = conn
        for part in ns.split('.'):
            coll = coll[part]
        
        docs = [__extract_fields(obj, fields) for obj in coll.find()]
        mongo_notification_handler.add(ns, docs)

def run(mongo_notification_handler, 
        mongo_host='localhost', 
        mongo_port=27017):
    assert isinstance(mongo_notification_handler, AMongoNotificationHandler)
    
    conn  = pymongo.Connection(mongo_host, mongo_port)
    db    = conn.local
    oplog = db.oplog.rs
    
    schemas = defaultdict(set)
    for o in db.fts.schemas.find():
        schemas[o['ns']] = schemas[o['ns']].union(o['fields'])
    
    progress_delta = 5
    progress_count = 100 / progress_delta
    
    state  = db.fts.find_one({'_id': 'state'})
    first  = True
    cursor = None
    count  = 0
    spec   = {}
    
    if state and 'ts' in state:
        first = oplog.find_one()
        
        if first['ts'].time > state['ts'].time and first['ts'].inc > state['ts'].inc:
            __init(conn, mongo_notification_handler, schemas)
        else:
            spec['ts'] = { '$gt': state['ts'] }
    else:
        __init(conn, mongo_notification_handler, schemas)
    
    # TODO: address async issue here..
    
    if not 'ts' in spec:
        try:
            # attempt to start pulling at the last occurrence of the target namespaces
            s = {"ns" : { "$in" : map(str, schemas.keys()) } }
            
            last = list(oplog.find(s).sort("$natural", -1).limit(1))[0]
            spec['ts'] = { '$gt': last['ts'] }
        except:
            # fallback to starting at the end of the oplog
            try:
                last = list(oplog.find().sort("$natural", -1).limit(1))[0]
                spec['ts'] = { '$gt': last['ts'] }
            except:
                # fallback to starting at the beginning of the oplog
                pass
    
    # poll the mongo oplog indefinitely
    while True:
        try:
            if not cursor or not cursor.alive:
                cursor = oplog.find(spec, tailable=True).sort("$natural", 1)
                count  = cursor.count()
            
            docs    = defaultdict(list)
            index   = 0
            
            for op in cursor:
                pprint(op)
                ns = op['ns']
                
                if ns in schemas:
                    spec['ts'] = { '$gt': op['ts'] }
                    #pprint(op)
                    
                    if op['op'] == 'd':
                        id = __extract_id(op['o']['_id'])
                        
                        mongo_notification_handler.delete(ns, id)
                    elif op['op'] in ['i', 'u']:
                        docs[ns].append(__extract_fields(op['o'], schemas[ns]))
                
                index += 1
                
                if first and (count < progress_count or 0 == (index % (count / progress_count))):
                    print "%s" % utils.getStatusStr(index, count)
            
            if docs:
                for ns, docs in docs.iteritems():
                    mongo_notification_handler.add(ns, docs)
            
            first = False
            db.fts.save({ '_id': 'state', 'ts': spec['ts']['$gt'] })
        except AutoReconnect as e:
            pass
        
        time.sleep(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mongo_host', dest='mongo_host', type=str, default="localhost",
                        help=("hostname or IP address of the Mongo instance to use"))
    parser.add_argument('-p', '--mongo_port', dest='mongo_port', type=int, default=27017,
                        help="port number of the Mongo instance")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    
    args    = parser.parse_args()
    handler = MongoNotificationHandler()
    
    run(handler, args.mongo_host, args.mongo_port)

