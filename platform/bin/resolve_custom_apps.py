#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import json, re, time, utils

from api_old.MongoStampedAPI        import MongoStampedAPI
from libs.apple             import AppleAPI
from crawler.match.EntityMatcher    import EntityMatcher

from gevent.pool            import Pool
from optparse               import OptionParser
from pprint                 import pprint

subtitles = [ "app", "App", "apps", "Apps", "iOS Apps", "iOS App", "Application", "ios app", "ios apps", "iOS App / Web Service", "iPhone App", "Iphone App", "Service", "Social Networks", "iphone app", "iphone apps", "Photography app", "iOS application", "Social service", "OCD/Hoarding Tools", "application", "Applications", "applications", ]
subtitles2 = list(a for a in subtitles)
subtitles2.extend(['Other', 'other'])

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
    matcher    = EntityMatcher(stampedAPI, options)
    appleAPI   = AppleAPI()
    
    rs = entityDB._collection.find({"sources.userGenerated.generated_by" : {"$exists" : True}, "subtitle" : {"$in" : subtitles }}, output=list)
    
    pool = Pool(1)
    seen = set()
    
    utils.log("processing %d entities" % len(rs))
    
    for result in rs:
        entity = entityDB._convertFromMongo(result)
        
        pool.spawn(handle_entity, entity, entityDB, matcher, appleAPI, seen, options)
        break
    
    pool.join()
    utils.log("done processing %d entities" % len(rs))

def handle_entity(entity, entityDB, matcher, appleAPI, seen, options):
    if entity.entity_id in seen:
        return
    
    title  = entity.titlel
    titles = [ title ]
    if title.endswith(' (app)'):
        title = entity.titlel[:-6]
        titles.append(title)
    
    rs = entityDB._collection.find({"sources.userGenerated.generated_by" : {"$exists" : True}, "subtitle" : {"$in" : subtitles2 }, "titlel" : {"$in" : titles}, }, output=list)
    
    if entity.entity_id in seen:
        return
    seen.add(entity.entity_id)
    
    entities = []
    for result in rs:
        entity2 = entityDB._convertFromMongo(result)
        if entity2 in seen:
            continue
        seen.add(entity2.entity_id)
        entities.append(entity2)
    
    results = appleAPI.search(term=entity.title, media='software', transform=True, limit=5)
    match   = False
    
    for result in results:
        entity2 = result.entity
        
        if entity2.title.lower() == title:
            match = True
            entity2.entity_id = entity.entity_id
            entity2.generated_by = entity.generated_by
            entity = entity2
            break
    
    entities = filter(lambda e: e.entity_id != entity.entity_id, entities)
    if len(entities) < 7:
        return
    
    utils.log("%s (%s) => %d (match=%s)" % (entity.title, entity.subtitle, len(entities), match))
    if match:
        matcher.resolveDuplicates(entity, entities)

if __name__ == '__main__':
    main()

