#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import stamped
import re, time, utils

from gevent.pool            import Pool
from libs.apple             import AppleAPI
from api.MongoStampedAPI        import MongoStampedAPI
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
    apple      = AppleAPI()
    
    rs = entityDB._collection.find({ "sources.apple.a_popular" : {"$exists" : True }}, output=list)
    
    pool = Pool(16)
    
    utils.log("processing %d entities" % len(rs))
    
    for result in rs:
        entity = entityDB._convertFromMongo(result)
        
        pool.spawn(handle_entity, entity, entityDB, apple, options)
    
    pool.join()

def handle_entity(entity, entityDB, apple, options):
    if entity.view_url is not None:
        return
    
    if entity.subcategory == 'album':
        results = apple.lookup(id=entity.aid, media='music', entity='song', transform=True)
        results = filter(lambda r: r.entity.subcategory == 'song', results)
        entity.tracks = list(result.entity.title for result in results)
        
        results = apple.lookup(id=entity.aid, media='music', entity='album', transform=True)
        results = filter(lambda r: r.entity.subcategory == 'album' and r.entity.aid == entity.aid, results)
    
    if entity.subcategory == 'song':
        results = apple.lookup(id=entity.aid, media='music', entity='song', transform=True)
        results = filter(lambda r: r.entity.subcategory == 'song' and r.entity.aid == entity.aid, results)
    
    if entity.subcategory == 'artist':
        results = apple.lookup(id=entity.aid, media='music', entity='allArtist', transform=True)
        results = filter(lambda r: r.entity.subcategory == 'artist' and r.entity.aid == entity.aid, results)
    
    if len(results) == 1:
        utils.log("SUCCESS: %s (%s)" % (entity.title, entity.subcategory))
        entity.view_url = results[0].entity.view_url
        
        if not options.noop:
            entityDB.updateEntity(entity)
    else:
        utils.log("FAIL: %s (%s)" % (entity.title, entity.subcategory))

if __name__ == '__main__':
    main()

