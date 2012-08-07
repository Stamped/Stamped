#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import math

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

class AppleEntitySink(AEntitySink):
    
    def __init__(self, options):
        AEntitySink.__init__(self, "AppleEntitySink")
        
        self.stampedAPI = MongoStampedAPI()
        self.matcher    = AppleEntityMatcher(self.stampedAPI, options)
    
    def _processItem(self, item):
        assert isinstance(item, Entity)
        #utils.log("merging item %s" % (item.title, ))
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
    
    parser.add_option("-r", "--ratio", default=None, type="string", 
        action="store", dest="ratio", 
        help="where this crawler fits in to a distributed stack")
    
    parser.add_option("-o", "--offset", default=0, 
        type="int", dest="offset", 
        help="start index of entities to import")
    
    parser.add_option("-l", "--limit", default=None, type="int", 
        help="limits the number of entities to import")
    
    (options, args) = parser.parse_args()
    Globals.options = options
    
    options.verbose = False
    options.mount   = True
    
    if options.db:
        utils.init_db_config(options.db)
    
    options.album_popularity_per_genre = AppleEPFAlbumPopularityPerGenreRelationalDB()
    options.song_popularity_per_genre  = AppleEPFSongPopularityPerGenreRelationalDB()
    
    options.album_popularity_per_genre.start()
    options.song_popularity_per_genre.start()
    options.album_popularity_per_genre.join()
    options.song_popularity_per_genre.join()
    
    options.count0 = options.album_popularity_per_genre.execute('SELECT COUNT(*) FROM "%s"' % \
                                                                options.album_popularity_per_genre.table).fetchone()[0]
    options.count1 = options.song_popularity_per_genre.execute('SELECT COUNT(*) FROM "%s"' % \
                                                                options.song_popularity_per_genre.table).fetchone()[0]
    options.count = options.count0 + options.count1
    
    if options.ratio:
        num, den = options.ratio.split('/')
        num, den = int(num), int(den)
        num, den = float(num), float(den)
        
        options.offset = int(math.floor((options.count * (num - 1)) / den))
        options.limit  = int(math.ceil(options.count / den) + 1)
        
        utils.log("ratio %s) offset=%d, limit=%d" % (options.ratio, options.offset, options.limit))
    else:
        if options.limit is None:
            options.limit = options.count
    
    return options

def main():
    options = parseCommandLine()
    
    """
    ret = utils.shell(r"grep 'class.*(AppleEPFRelationalDB' sources/dumps/AppleEPFRelationalDB.py | sed 's/class \([^(]*\)(.*/\1/g'")
    ret = map(lambda r: r.strip() + "()", ret[0].split('\n'))
    
    for r in ret:
        cls = eval(r)
        
        cls._run()
        #cls.start()
        #cls.join()
        cls.close()
    """
    
    sink = AppleEntitySink(options)
    appleAPI = AppleAPI(country='us')
    
    pool   = Pool(32)
    offset = 0
    done   = 0
    
    all_artists = set()
    all_albums  = set()
    all_songs   = set()
    
    count = options.count0
    rows  = options.album_popularity_per_genre.execute('SELECT * FROM "%s"' % \
                                                       options.album_popularity_per_genre.table)
    rows  = list(rows)
    
    # loop through all albums
    utils.log("[%s] parsing %d rows" % ('albums', count))
    for i in xrange(len(rows)):
        if offset < options.offset: offset += 1; continue
        if options.limit is not None and done > options.limit: break
        done += 1
        
        row = rows[i]
        row = options.album_popularity_per_genre._format_result(row)
        pool.spawn(parse_album, row, appleAPI, sink, pool, all_artists, all_albums, all_songs)
        
        if options.limit <= 100 or ((done - 1) % (options.limit / 100)) == 0:
            utils.log("[%s] done parsing %s" % ('albums', utils.getStatusStr(done, options.limit)))
    
    count = options.count1
    rows  = options.song_popularity_per_genre.execute('SELECT * FROM "%s"' % \
                                                      options.song_popularity_per_genre.table)
    rows  = list(rows)
    
    # loop through all songs
    utils.log("[%s] parsing %d rows" % ('songs', count))
    for i in xrange(len(rows)):
        if offset < options.offset: offset += 1; continue
        if options.limit is not None and done > options.limit: break
        done += 1
        
        row = rows[i]
        row = options.song_popularity_per_genre._format_result(row)
        pool.spawn(parse_song, row, appleAPI, sink, pool, all_artists, all_albums, all_songs)
        
        if options.limit <= 100 or ((done - 1) % (options.limit / 100)) == 0:
            utils.log("[%s] done parsing %s" % ('songs', utils.getStatusStr(done, options.limit)))
    
    pool.join()
    
    print "artists: %d" % len(all_artists)
    print "albums:  %d" % len(all_albums)
    print "songs:   %d" % len(all_songs)

def parse_album(row, appleAPI, sink, pool, all_artists, all_albums, all_songs):
    results = appleAPI.lookup(id=row.album_id, media='music', entity='allArtist', transform=True)
    
    artists = filter(lambda r: r.entity.subcategory == 'artist', results)
    assert 1 >= len(artists)
    
    for artist in artists:
        add_artist(artist.entity, appleAPI, sink, pool, all_artists, all_albums, all_songs)
    
    albums  = filter(lambda r: r.entity.subcategory == 'album', results)
    assert 1 >= len(albums)
    
    for album in albums:
        add_album(album.entity, appleAPI, sink, pool, all_artists, all_albums, all_songs)

def parse_song(row, appleAPI, sink, pool, all_artists, all_albums, all_songs):
    results = appleAPI.lookup(id=row.song_id, transform=True)
    if 0 == len(results):
        return
    
    songs   = filter(lambda r: r.entity.subcategory == 'song', results)
    assert 1 >= len(songs)
    song    = songs[0]
    
    add_song(song.entity, appleAPI, sink, pool, all_artists, all_albums, all_songs)

def add_album(entity, appleAPI, sink, pool, all_artists, all_albums, all_songse):
    assert entity.subcategory == 'album'
    if int(entity.aid) in all_albums: return
    all_albums.add(int(entity.aid))
    
    utils.log("adding album %s" % entity.title)
    results = appleAPI.lookup(id=entity.aid, media='music', entity='song', transform=True)
    results = filter(lambda r: r.entity.subcategory == 'song', results)
    
    entity.tracks = list(result.entity.title for result in results)
    
    #for result in results:
    #    add_song(result.entity, appleAPI, sink, pool, all_artists, all_albums, all_songs)
    
    sink._processItem(entity)

def add_artist(entity, appleAPI, sink, pool, all_artists, all_albums, all_songs):
    assert entity.subcategory == 'artist'
    if int(entity.aid) in all_artists: return
    all_artists.add(int(entity.aid))
    
    utils.log("adding artist %s" % entity.title)
    results = appleAPI.lookup(id=entity.aid, media='music', entity='album', limit=200, transform=True)
    results = filter(lambda r: r.entity.subcategory == 'album', results)
    
    for result in results:
        add_album(result.entity, appleAPI, sink, pool, all_artists, all_albums, all_songs)
    
    if len(results) > 0:
        albums = []
        for result in results:
            schema = ArtistAlbumsSchema()
            schema.album_name = result.entity.title
            schema.album_id   = result.entity.aid
            albums.append(schema)
        
        entity.albums = albums
        images = results[0].entity.images
        for k in images:
            entity[k] = images[k]
    
    results = appleAPI.lookup(id=entity.aid, media='music', entity='song', limit=200, transform=True)
    results = filter(lambda r: r.entity.subcategory == 'song', results)
    
    #for result in results:
    #    add_song(result.entity, appleAPI, sink, pool, all_artists, all_albums, all_songs)
    
    songs = []
    for result in results:
        schema = ArtistSongsSchema()
        schema.song_id   = result.entity.aid
        schema.song_name = result.entity.title
        songs.append(schema)
    
    entity.songs = songs
    try:
        sink._processItem(entity)
    except Exception, e:
        utils.printException()
        pprint(entity)

def add_song(entity, appleAPI, sink, pool, all_artists, all_albums, all_songs):
    assert entity.subcategory == 'song'
    if int(entity.aid) in all_songs: return
    all_songs.add(int(entity.aid))
    
    utils.log("adding song %s" % entity.title)
    sink._processItem(entity)

if __name__ == '__main__':
    main()

