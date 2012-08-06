#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import pymongo, os, utils

from subprocess import Popen, PIPE
from api.db.mongodb.AMongoCollection import MongoDBConfig

def main():
    import argparse
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-d', '--drop', action="store_true", default=False,
                        help="drop existing collections before importing")
    
    parser.add_argument("-s", "--source", default=None, type=str, help="db to import from")
    
    parser.add_argument("-t", "--target", default=None, type=str, help="db to import to")
    
    args = parser.parse_args()
    host, port = utils.get_db_config(args.source)
    
    utils.log("SOURCE: %s:%s" % (host, port))
    
    old_host        = host
    old_connection  = pymongo.Connection(host, port)
    old_database    = old_connection['stamped']
    collections     = old_database.collection_names()
    
    new_host        = args.target
    if new_host is None:
        dest            = MongoDBConfig.getInstance()
        new_host        = dest.host
    
    utils.log("DEST: %s:%s" % (new_host, port))
    
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
            ret = mongoExportImport(collection, old_host, new_host)
            
            if 0 == ret:
                print 'COMPLETE'
            else:
                print "ERROR restoring collection '%s'" % collection
        
        print 
    
    try:
        utils.runMongoCommand('db.runCommand( {createCollection:"logs", capped:true, size:500000} )')
    except:
        utils.printException()

def mongoExportImport(collection, old_host, new_host):
    cmdExport = "mongodump --db stamped --collection %s --host %s --out /stamped/tmp" % \
                (collection, old_host)
    cmdImport = "mongorestore --db stamped --collection %s --host %s /stamped/tmp/stamped/%s.bson" % \
                (collection, new_host, collection)
    
    out = open("/stamped/tmp/convert_%s.log" % collection, "w")
    cmd = "%s && %s && rm -rf /stamped/tmp/stamped/%s.bson" % \
            (cmdExport, cmdImport, collection)
    pp  = Popen(cmd, shell=True, stdout=out, stderr=out)
    
    return pp.wait()

if __name__ == '__main__':  
    main()

