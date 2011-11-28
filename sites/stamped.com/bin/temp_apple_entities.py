#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import init
import json, re, time, utils

from MongoStampedAPI    import MongoStampedAPI

from gevent.pool        import Pool
from optparse           import OptionParser
from pprint             import pprint

subtitles = [ "app", "App", "apps", "Apps", "iOS Apps", "iOS App", "Application", "Software", "ios app", "ios apps", "iOS App / Web Service", "iPhone App", "Iphone App", "Service", "Social Networks", "iphone app", "iphone apps", "Photography app", "iOS application", "Social service", "OCD/Hoarding Tools", "Feelings", "application", "software", "Software", "Applications", "applications", "Other", "other"]

def parseCommandLine():
    usage   = "Usage: %prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", help="db to connect to")
    
    parser.add_option("-n", "--noop", default=False, action="store_true", 
        help="run in noop mode without modifying anything")
    
    parser.add_option("-v", "--verbose", default=False, action="store_true", 
        help="enable verbose logging")
    
    (options, args) = parser.parse_args()
    
    if options.db:
        utils.init_db_config(options.db)
    
    return (options, args)

def main():
    options, args = parseCommandLine()
    
    stampedAPI = MongoStampedAPI()
    entityDB   = stampedAPI._entityDB
    
    rs = entityDB._collection.find({"sources.userGenerated.generated_by" : {"$exists" : True}, "subtitle" : {"$in" : subtitles }}, output=list)
    
    pool = Pool(16)
    seen = set()
    
    utils.log("processing %d entities" % len(rs))
    
    for result in rs:
        entity = entityDB._convertFromMongo(result)
        
        pool.spawn(handle_entity, entity, entityDB, seen, options)
    
    pool.join()
    utils.log("done processing %d entities" % len(rs))

def handle_entity(entity, entityDB, seen, options):
    if entity.entity_id in seen:
        return
    seen.add(entity.entity_id)
    
    rs = entityDB._collection.find({"sources.userGenerated.generated_by" : {"$exists" : True}, "subtitle" : {"$in" : subtitles }, "titlel" : entity.titlel, }, output=list)
    
    entities = []
    for result in rs:
        entity2 = entityDB._convertFromMongo(result)
        if entity2 in seen:
            continue
        seen.add(entity2.entity_id)
        entities.append(entity2)
    
    utils.log("%s => %d" % (entity.title, len(entities)))
    """
    if not options.noop:
        entityDB.updateEntity(entity)
    """

if __name__ == '__main__':
    main()

