#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import pymongo, os, utils

from subprocess import Popen, PIPE
from api.db.mongodb.AMongoCollection import MongoDBConfig

OLD_HOST            = None
NEW_HOST            = None

def main():
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-D', '--drop', action="store_true", default=False,
                        help="drop existing collections before importing")
    
    parser.add_argument("-s", "--source", default=None, type=str, help="db to import from")
    
    args = parser.parse_args()
    host, port = utils.get_db_config(args.source)
    OLD_HOST        = host
    
    old_connection  = pymongo.Connection(host, port)
    old_database    = old_connection['stamped']
    collections     = old_database.collection_names()
    dest            = MongoDBConfig.getInstance()
    NEW_HOST        = dest.host
    
    if not os.path.isdir('/stamped/tmp/stamped/'):
       os.makedirs('/stamped/tmp/stamped')
    
    ignore = set([
        'tempentities', 'logs', 'logstats', 
    ])
    
    for collection in collections:
        print 'RUN %s' % collection
        
        if collection in ignore:
            print 'PASS'
        else:
            ret = mongoExportImport(collection)
            
            if 0 == ret:
                print 'COMPLETE'
            else:
                print "ERROR restoring collection '%s'" % collection
        
        print 
    
    convertEntities()
    
    try:
        utils.runMongoCommand('db.runCommand( {createCollection:"logs", capped:true, size:500000} )')
    except:
        utils.printException()

def mongoExportImport(collection):
    cmdExport = "mongodump --db stamped --collection %s --host %s --out /stamped/tmp" % \
                (collection, OLD_HOST)
    cmdImport = "mongorestore --db stamped --collection %s --host %s /stamped/tmp/stamped/%s.bson" % \
                (collection, NEW_HOST, collection)
    
    out = open("/stamped/tmp/convert_%s.log" % collection, "w")
    cmd = "%s && %s && rm -rf /stamped/tmp/stamped/%s.bson" % \
            (cmdExport, cmdImport, collection)
    pp  = Popen(cmd, shell=True, stdout=out, stderr=out)
    
    return pp.wait()

def mongoExportJSON(collection):
    collection = collection.lower()
    cmdExport = "mongoexport --db stamped --collection %s --host %s --out /stamped/tmp/stamped/%s.json" % \
                (collection, OLD_HOST, collection)
    pp = Popen(cmdExport, shell=True, stdout=PIPE)
    return pp.wait()

def mongoImportJSON(collection):
    collection = collection.lower()
    cmdImport = "mongoimport --db stamped --collection %s --host %s /stamped/tmp/stamped/%s_out.json" % \
                (collection, NEW_HOST, collection)
    pp = Popen(cmdImport, shell=True, stdout=PIPE)
    return pp.wait()

def convertEntities():
    # no-op
    return

if __name__ == '__main__':  
    main()

