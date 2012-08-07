#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import re, time, utils

from gevent.pool            import Pool
from api_old.MongoStampedAPI        import MongoStampedAPI
from crawler.match.EntityMatcher    import EntityMatcher
from optparse               import OptionParser
from pprint                 import pprint

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
    appleAPI   = AppleAPI(country='us')
    matcher    = EntityMatcher(stampedAPI)
    
    rs = entityDB._collection.find({ "sources.apple.a_popular" : True, "subcategory" : "app"}, output=list)
    pool = Pool(16)
    
    utils.log("processing %d entities" % len(rs))
    
    for result in rs:
        entity = entityDB._convertFromMongo(result)
        
        pool.spawn(handle_entity, entity, entityDB, appleAPI, matcher, options)
    
    pool.join()

def handle_entity(entity, entityDB, appleAPI, matcher, options):
    results = appleAPI.lookup(id=entity.aid, media='software', entity=None, transform=True)
    results = filter(lambda r: r.entity.subcategory == 'app', results)
    
    found = False
    if len(results) == 1:
        entity2 = results[0].entity
        
        if entity2.title == entity1.title:
            found = True
            entity.image = entity2.image
            
            if entity2.screenshots is not None:
                entity.details.media.screenshots = entity2.screenshots
            
            if not options.noop:
                entityDB.save(entity)
    
    if not found:
        utils.log("error: unable to convert '%s' (%s)" % (entity.title, entity.aid))

if __name__ == '__main__':
    main()

