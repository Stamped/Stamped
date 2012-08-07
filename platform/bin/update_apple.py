#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import re, time, utils

from gevent.pool            import Pool
from libs.applerss          import AppleRSS
from api_old.MongoStampedAPI        import MongoStampedAPI
from optparse               import OptionParser
from pprint                 import pprint
from datetime               import datetime
from libs.iTunes            import globaliTunes
import logs

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
    
    parser.add_option("-m", "--musiconly", default=False, action="store_true", 
        help="only parse music feeds")
    
    parser.add_option("-a", "--appsonly", default=False, action="store_true", 
        help="only parse app feeds")

    parser.add_option("-q", "--qps", default=2, type="int", dest="max_qps",
        action="store", help="max QPS sent to iTunes")
    
    (options, args) = parser.parse_args()
    
    if options.db:
        utils.init_db_config(options.db)
    
    return (options, args)

def main():
    options, args = parseCommandLine()

    globaliTunes().setMaxQps(options.max_qps)

    stampedAPI = MongoStampedAPI()
    appleRSS = AppleRSS()

    itunes_ids = set()
    
    # music feed popularity prioritized by genre
    music_feeds = [
        { 'limit' : 150,               'name' : 'overall' },
        { 'limit' : 50,  'genre' : 18, 'name' : 'hip-hop', }, 
        { 'limit' : 50,  'genre' : 14, 'name' : 'pop', }, 
        { 'limit' : 50,  'genre' : 20, 'name' : 'alternative', }, 
        { 'limit' : 50,  'genre' : 21, 'name' : 'rock', }, 
        { 'limit' : 50,  'genre' : 6,  'name' : 'country', }, 
        { 'limit' : 25,  'genre' : 15, 'name' : 'R&B / Soul', }, 
        { 'limit' : 25,  'genre' : 16, 'name' : 'soundtrack', }, 
        { 'limit' : 25,  'genre' : 17, 'name' : 'dance', }, 
        { 'limit' : 25,  'genre' : 5,  'name' : 'classical', }, 
        { 'limit' : 10,  'genre' : 24, 'name' : 'reggae', }, 
        { 'limit' : 10,  'genre' : 22, 'name' : 'inspirational', }, 
        { 'limit' : 10,  'genre' : 19, 'name' : 'world', }, 
        { 'limit' : 10,  'genre' : 13, 'name' : 'new age', }, 
        { 'limit' : 10,  'genre' : 12, 'name' : 'latin', }, 
        { 'limit' : 10,  'genre' : 11, 'name' : 'jazz', }, 
        { 'limit' : 10,  'genre' : 9,  'name' : 'opera', }, 
        { 'limit' : 10,  'genre' : 8,  'name' : 'holiday', }, 
        { 'limit' : 10,  'genre' : 7,  'name' : 'electronic', }, 
        { 'limit' : 10,  'genre' : 3,  'name' : 'comedy', }, 
        { 'limit' : 10,  'genre' : 2,  'name' : 'blues', }, 
    ]
    
    if not options.appsonly:
        utils.log("processing %d music feeds" % (2 * len(music_feeds), ))
        
        for feed in music_feeds:
            handle_music_feed(feed, stampedAPI, appleRSS, itunes_ids, options)
    
    app_feeds = [
        { 'limit' : 150,                    'name' : 'overall' },
        { 'limit' : 20,  'genre' : 6018,    'name' : 'books', }, 
        { 'limit' : 20,  'genre' : 6000,    'name' : 'business', }, 
        { 'limit' : 20,  'genre' : 6017,    'name' : 'education', }, 
        { 'limit' : 50,  'genre' : 6016,    'name' : 'entertainment', }, 
        { 'limit' : 20,  'genre' : 6015,    'name' : 'finance', }, 
        { 'limit' : 25,  'genre' : 6013,    'name' : 'health & fitness', }, 
        { 'limit' : 25,  'genre' : 6012,    'name' : 'lifestyle', }, 
        { 'limit' : 25,  'genre' : 6020,    'name' : 'medical', }, 
        { 'limit' : 30,  'genre' : 6011,    'name' : 'music', }, 
        { 'limit' : 25,  'genre' : 6010,    'name' : 'navigation', }, 
        { 'limit' : 50,  'genre' : 6009,    'name' : 'news', }, 
        { 'limit' : 25,  'genre' : 6021,    'name' : 'newsstand', }, 
        { 'limit' : 50,  'genre' : 6008,    'name' : 'photo & video', }, 
        { 'limit' : 25,  'genre' : 6007,    'name' : 'productivity', }, 
        { 'limit' : 25,  'genre' : 6006,    'name' : 'reference', }, 
        { 'limit' : 50,  'genre' : 6005,    'name' : 'social networking', }, 
        { 'limit' : 25,  'genre' : 6004,    'name' : 'sports', }, 
        { 'limit' : 50,  'genre' : 6003,    'name' : 'travel', }, 
        { 'limit' : 20,  'genre' : 6002,    'name' : 'utilities', }, 
        { 'limit' : 10,  'genre' : 6001,    'name' : 'weather', }, 
    ]
    
    if not options.musiconly:
        utils.log("processing %d app feeds" % (3 * len(app_feeds), ))
        
        for feed in app_feeds:
            # Handle feeds synchronously, there's already plenty of parallelism within the handling of each feed.
            handle_app_feed(feed, stampedAPI, appleRSS, itunes_ids, options)


def handle_music_feed(feed, stampedAPI, appleRSS, itunes_ids, options):
    name = feed['name']
    del feed['name']
    
    utils.log("processing music feed '%s'" % name)
    feed['transform'] = 2
    
    albums = appleRSS.get_top_albums(**feed)
    songs  = appleRSS.get_top_songs(**feed)
    
    utils.log("retrieved %d albums and %d songs from feed '%s'" % (len(albums), len(songs), name))
    
    albums.extend(songs)
    entities = albums

    def import_entity(entity):
        itunes_id = int(entity.sources.itunes_id)
        if itunes_id in itunes_ids:
            return
        
        itunes_ids.add(itunes_id)
        utils.log(u"(%s) %s (%s)" % (entity.subcategory, entity.title, entity.sources.itunes_id))
        entity.last_popular = datetime.now()

        if options.noop:
            pprint(entity)
        else:
            output = u"About to merge music entity" + entity.title + u"with iTunes ID" + entity.sources.itunes_id
            logs.info(output)
            stampedAPI.mergeEntity(entity)
            output = u"Stored music entity" + entity.title + u"with iTunes ID" + entity.sources.itunes_id
            logs.info(output)

    pool = Pool(16)
    for entity in entities:
        pool.spawn(import_entity, entity)
    pool.join()

def handle_app_feed(feed, stampedAPI, appleRSS, itunes_ids, options):
    name = feed['name']
    del feed['name']
    
    utils.log("processing app feed '%s'" % name)
    feed['transform'] = 2
    
    apps  = appleRSS.get_top_free_apps(**feed)
    apps2 = appleRSS.get_top_paid_apps(**feed); apps.extend(apps2)
    apps2 = appleRSS.get_top_grossing_apps(**feed); apps.extend(apps2)
    
    def import_entity(entity):
        itunes_id = int(entity.sources.itunes_id)
        if itunes_id in itunes_ids:
            return
        
        itunes_ids.add(itunes_id)
        
        utils.log("(%s) %s (%s)" % (entity.subcategory, entity.title, entity.sources.itunes_id))

        # TODO: In order to be used, this actually needs to be exposed in the ResolverObject interface
        # and used by enrichEntityWithProxy implementations!
        entity.last_popular = datetime.now()
        
        if options.noop:
            pprint(entity)
        else:
            output = u"About to merge app entity" + entity.title + u"with iTunes ID" +entity.sources.itunes_id
            logs.info(output)
            stampedAPI.mergeEntity(entity)
            output = u"Stored app entity" + entity.title + u"with iTunes ID" + entity.sources.itunes_id
            logs.info(output)

    pool = Pool(16)
    for entity in apps:
        pool.spawn(import_entity, entity)
    pool.join()

if __name__ == '__main__':
    main()

