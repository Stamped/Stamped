#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from crawler.sources.dumps.AppleEPFRelationalDB import *
from crawler.match.IDBasedEntityMatchers import AppleEntityMatcher

from api_old.AEntitySink            import AEntitySink
from api_old.MongoStampedAPI        import MongoStampedAPI
from crawler.match.EntityMatcher    import EntityMatcher
from api_old.Schemas                import *
from gevent.pool            import Pool
from libs.apple             import AppleAPI
from optparse               import OptionParser
from pprint                 import pprint

#-----------------------------------------------------------

ret = utils.shell(r"grep 'class.*(AppleEPFRelationalDB' sources/dumps/AppleEPFRelationalDB.py | sed 's/class \([^(]*\)(.*/\1/g'")
ret = map(lambda r: r.strip() + "()", ret[0].split('\n'))
dbs = {}

for r in ret:
    cls = eval(r)
    cls._run()
    dbs[cls._filename] = cls

class AppleEntitySink(AEntitySink):
    
    def __init__(self, options):
        AEntitySink.__init__(self, "AppleEntitySink")
        
        self.stampedAPI = MongoStampedAPI()
        self.matcher    = AppleEntityMatcher(self.stampedAPI, options)
    
    def _processItem(self, item):
        assert isinstance(item, Entity)
        utils.log("merging item %s" % (item.title, ))
        
        self.matcher.addOne(item, override=True)
    
    def _processItems(self, items):
        for item in items:
            self._processItem(item)

def parseCommandLine():
    usage   = "Usage: %prog [options] [sources]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", 
        help="db to connect to for output")
    
    parser.add_option("-n", "--noop", default=False, action="store_true", 
        help="run the dedupper in noop mode without modifying anything")
    
    (options, args) = parser.parse_args()
    Globals.options = options
    
    if options.db:
        utils.init_db_config(options.db)
    
    return options

def main():
    options = parseCommandLine()
    
    sink = AppleEntitySink(options)
    appleAPI = AppleAPI(country='us')
    
    all_artists = set()
    all_albums  = set()
    all_songs   = set()
    
    pool = Pool(16)
    
    """
    count = dbs['album_popularity_per_genre'].execute('SELECT COUNT(*) FROM "%s"' % \
                                                      dbs['album_popularity_per_genre'].table).fetchone()[0]
    
    rows  = dbs['album_popularity_per_genre'].execute('SELECT * FROM "%s"' % \
                                                      dbs['album_popularity_per_genre'].table)
    rows  = list(rows)
    
    utils.log("[%s] parsing %d rows" % ('albums', count))
    for i in xrange(len(rows)):
        row = rows[i]
        row = dbs['album_popularity_per_genre']._format_result(row)
        pool.spawn(parse_album, row, appleAPI, sink, pool, all_artists, all_albums, all_songs)
        
        if count <= 100 or ((i - 1) % (count / 100)) == 0:
            utils.log("[%s] done parsing %s" % ('albums', utils.getStatusStr(i, count)))
        break
    """
    
    count = dbs['song_popularity_per_genre'].execute('SELECT COUNT(*) FROM "%s"' % \
                                                     dbs['song_popularity_per_genre'].table).fetchone()[0]
    rows  = dbs['song_popularity_per_genre'].execute('SELECT * FROM "%s"' % \
                                                     dbs['song_popularity_per_genre'].table)
    rows  = list(rows)
    
    utils.log("[%s] parsing %d rows" % ('songs', count))
    for i in xrange(len(rows)):
        row = rows[i]
        row = dbs['song_popularity_per_genre']._format_result(row)
        pool.spawn(parse_song, row, appleAPI, sink, pool, all_artists, all_albums, all_songs)
        
        if count <= 100 or ((i - 1) % (count / 100)) == 0:
            utils.log("[%s] done parsing %s" % ('songs', utils.getStatusStr(i, count)))
        break
    
    pool.join()
    
    print "artists: %d" % len(all_artists)
    print "albums:  %d" % len(all_albums)
    print "songs:   %d" % len(all_songs)

def parse_album(row, appleAPI, sink, pool, all_artists, all_albums, all_songs):
    album = dbs['collection'].get_row("collection_id", row.album_id, transform=True)
    pprint(album.value)

def parse_song(row, appleAPI, sink, pool, all_artists, all_albums, all_songs):
    #song = dbs['song'].get_row("song_id", row.song_id, transform=True)
    artist_song = dbs['artist_song'].get_row("song_id", row.song_id)
    
    add_artist(artist_song.artist_id, appleAPI, sink, pool, all_artists, all_albums, all_songs)

def add_artist(aid, appleAPI, sink, pool, all_artists, all_albums, all_songs):
    if aid in all_artists: return
    all_artists.add(aid)
    
    entity = dbs['artist'].get_row("artist_id", aid, transform=True)
    
    # handle albums
    collections = dbs['artist_collection'].get_rows("artist_id", aid)
    albums = []
    
    def _parse_album(collection):
        album = dbs['collection'].get_row("collection_id", collection.collection_id, transform=True)
        
        if album is not None:
            if album.artist_display_name is None or 0 == len(album.artist_display_name):
                album.artist_display_name = entity.title
            
            albums.append(album)
    
    for collection in collections:
        _parse_album(collection)
    
    if len(albums) > 0:
        out_albums = []
        
        for album in albums:
            add_album(album, appleAPI, sink, pool, all_artists, all_albums, all_songs)
            
            schema = ArtistAlbumsSchema()
            schema.album_name = album.title
            schema.album_id   = album.aid
            out_albums.append(schema)
        
        entity.albums = out_albums
    
    """
    # handle songs
    songs  = dbs['artist_song'].get_rows("artist_id", aid)
    songs2 = []
    
    for song in songs:
        song = dbs['song'].get_row("song_id", song.song_id, transform=True)
        
        if song is not None:
            if song.artist_display_name is None or 0 == len(song.artist_display_name):
                song.artist_display_name = entity.title
            
            songs2.append(album)
    
    if len(songs2) > 0:
        out_songs = []
        
        for song in songs2:
            add_song(song, appleAPI, sink, pool, all_artists, all_albums, all_songs)
    """
    
    pprint(entity.value)

def add_album(album, appleAPI, sink, pool, all_artists, all_albums, all_songs):
    if album.aid in all_albums: return
    all_albums.add(album.aid)
    
    

if __name__ == '__main__':
    main()

