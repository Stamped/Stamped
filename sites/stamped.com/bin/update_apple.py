#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import init
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
    
    # feed popularity prioritized by genre
    feeds = [
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
    
    utils.log("processing %d feeds" % (2 * len(feeds), ))
    
    for feed in feeds:
        pool.spawn(handle_feed, feed, matcher, appleRSS, aids, options)
    
    pool.join()

def handle_feed(feed, matcher, appleRSS, aids, options):
    name = feed['name']
    del feed['name']
    
    utils.log("processing feed '%s'" % name)
    
    albums = appleRSS.get_top_albums(**feed)
    songs  = appleRSS.get_top_songs(**feed)
    
    utils.log("retrieved %d albums and %d songs from feed '%s'" % (len(albums), len(songs), name))
    
    albums.extend(songs)
    entities = albums
    
    for entity in entities:
        entity_id = int(entity.aid)
        if entity_id in aids:
            continue
        aids.add(entity_id)
        
        utils.log("%s) %s (%s)" % (entity.subcategory, entity.title, entity.aid))
        matcher.addOne(entity)
        
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
                
                utils.log("%s) %s (%s)" % (entity.subcategory, entity.title, entity.aid))
                matcher.addOne(artist)

if __name__ == '__main__':
    main()

