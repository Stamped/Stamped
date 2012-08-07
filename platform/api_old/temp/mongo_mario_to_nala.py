#!/usr/bin/env python

import Globals
import pymongo, json, codecs, os, sys, bson, utils, unicodedata
from subprocess import Popen, PIPE

OLD_HOST            = "10.8.197.216"
NEW_HOST            = "10.104.7.184"

def main():
    old_connection  = pymongo.Connection(OLD_HOST, 27017)
    new_connection  = pymongo.Connection(NEW_HOST, 27017)
    
    old_database    = old_connection['stamped']
    new_database    = new_connection['stamped']
    
    collections     = old_database.collection_names()
    
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

