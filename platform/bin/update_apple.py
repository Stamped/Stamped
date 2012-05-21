#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import re, time, utils

from gevent.pool            import Pool
from match.EntityMatcher    import EntityMatcher
from libs.applerss          import AppleRSS
from MongoStampedAPI        import MongoStampedAPI
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
    
    parser.add_option("-m", "--musiconly", default=False, action="store_true", 
        help="only parse music feeds")
    
    parser.add_option("-a", "--appsonly", default=False, action="store_true", 
        help="only parse app feeds")
    
    (options, args) = parser.parse_args()
    
    if options.db:
        utils.init_db_config(options.db)
    
    return (options, args)

def main():
    options, args = parseCommandLine()
    
    stampedAPI = MongoStampedAPI()
    matcher    = EntityMatcher(stampedAPI, options)
    appleRSS   = AppleRSS()
    
    pool = Pool(8)
    aids = set()
    
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
            pool.spawn(handle_music_feed, feed, matcher, appleRSS, aids, options)
    
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
            pool.spawn(handle_app_feed, feed, matcher, appleRSS, aids, options)
    
    pool.join()

def handle_music_feed(feed, matcher, appleRSS, aids, options):
    name = feed['name']
    del feed['name']
    
    utils.log("processing music feed '%s'" % name)
    feed['transform'] = 2
    
    albums = appleRSS.get_top_albums(**feed)
    songs  = appleRSS.get_top_songs(**feed)
    
    utils.log("retrieved %d albums and %d songs from feed '%s'" % (len(albums), len(songs), name))
    
    albums.extend(songs)
    entities = albums
    
    for entity in entities:
        aid = int(entity.aid)
        if aid in aids:
            continue
        
        aids.add(aid)
        utils.log("(%s) %s (%s)" % (entity.subcategory, entity.title, entity.aid))
        entity.a_popular = True
        
        if entity.subcategory == 'album':
            results = appleRSS._apple.lookup(id=entity.aid, media='music', entity='song', transform=True)
            results = filter(lambda r: r.entity.subcategory == 'song', results)
            entity.tracks = list(result.entity.title for result in results)
        
        if options.noop:
            pprint(entity)
        else:
            matcher.addOne(entity)
        
        # attempt to lookup artist for this entity
        if entity.artist_id is not None:
            artist_id = int(entity.artist_id)
            if artist_id in aids:
                continue
            
            results = appleRSS._apple.lookup(id=str(artist_id), media='music', entity='allArtist', transform=True)
            artists = filter(lambda r: r.entity.subcategory == 'artist', results)
            
            for artist in artists:
                artist = artist.entity
                
                artist_id = int(artist.aid)
                if artist_id in aids:
                    continue
                
                aids.add(artist_id)
                appleRSS.parse_artist(artist)
                
                utils.log("%s) %s (%s)" % (artist.subcategory, artist.title, artist.aid))
                artist.a_popular = True
                if not options.noop:
                    matcher.addOne(artist)

def handle_app_feed(feed, matcher, appleRSS, aids, options):
    name = feed['name']
    del feed['name']
    
    utils.log("processing app feed '%s'" % name)
    feed['transform'] = 2
    
    apps  = appleRSS.get_top_free_apps(**feed)
    apps2 = appleRSS.get_top_paid_apps(**feed); apps.extend(apps2)
    apps2 = appleRSS.get_top_grossing_apps(**feed); apps.extend(apps2)
    
    for entity in apps:
        aid = int(entity.aid)
        if aid in aids:
            continue
        
        aids.add(aid)
        
        utils.log("%s) %s (%s)" % (entity.subcategory, entity.title, entity.aid))
        entity.a_popular = True
        
        if options.noop:
            pprint(entity)
        else:
            matcher.addOne(entity)

if __name__ == '__main__':
    main()

