#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from crawler.sources.dumps import epf
import sqlite3, string
from crawler.sources.dumps import CSVUtils

try:
    import psycopg2
    import psycopg2.extensions

    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
except ImportError:
    utils.log("Warning: missing required psycopg2 module")

from pprint       import pprint
from utils        import AttributeDict
from crawler.sources.dumps.AppleEPFDump import AAppleEPFDump

class AppleEPFRelationalDB(AAppleEPFDump):
    def __init__(self, name, filename, index=None, primary=None):
        AAppleEPFDump.__init__(self, name, None, [ ], filename)
        self.index   = index
        self.primary = primary
    
    def _run(self):
        utils.log("[%s] initializing" % self)
        f, numLines, filename = self._open_file(countLines=False)
        
        table_format = epf.parse_table_format(f, filename)
        self.table_format = table_format
        
        stale = False
        self._buffer = []
        self._buffer_threshold = 1024
        
        # determine whether or not the db table already exists and attempt to 
        # determine if it's up-to-date s.t. we won't recalculate it if it'd 
        # be unnecessary.
        try:
            row0 = self.execute('SELECT * FROM %s LIMIT 1' % (self.table, ), error_okay=True).fetchone()
            
            if row0 is None:
                stale = True
            elif len(row0) != len(dict(table_format.cols)):
                stale = True
        except Exception:
            self.conn.rollback()
            #utils.printException()
            stale = True
            pass
        
        #f.close(); self._output.put(StopIteration); return
        
        if not stale:
            # table is usable as-is
            utils.log("[%s] %s.%s doesn't need to be recomputed" % (self, self.dbpath, self.table))
        else:
            utils.log("[%s] opening '%s'" % (self, self._filename))
            
            numLines = max(0, utils.getNumLines(f) - 8)
            table_format = epf.parse_table_format(f, filename)
            self.table_format = table_format
            
            utils.log("[%s] parsing ~%d rows from '%s'" % (self, numLines, self._filename))
            
            # initialize table
            cols  = []
            
            # currently disabling primary keys for most tables
            found_primary = False #(len(table_format.primary_keys) != 1)
            
            for col in table_format.cols:
                cols.append('')
            
            for col in table_format.cols:
                primary = ""
                if not found_primary and col == self.primary and not self._sqlite:
                #if not found_primary and col in table_format.primary_keys:
                    # TODO: handle the common case of multiple primary keys, which sqlite3 does not support
                    # TODO: defining the primary key here as opposed to after insertion is much slower!
                    primary = " PRIMARY KEY"
                    found_primary = True
                
                col2  = table_format.cols[col]
                col_type = col2['type']
                
                if not self._sqlite:
                    # perform mapping between some MySQL types that Apple uses and 
                    # their postgres equivalents
                    if col_type == 'DATETIME':
                        col_type = 'VARCHAR(100)'
                    elif col_type == 'LONGTEXT':
                        col_type = 'VARCHAR(4000)'
                
                text  = "%s %s%s" % (col, col_type, primary)
                index = col2['index']
                cols[index] = text
            
            args = string.joinfields(cols, ', ')
            self.execute("DROP TABLE %s" % (self.table, ), error_okay=True)
            self.execute("CREATE TABLE %s (%s)" % (self.table, args), verbose=True)
            
            if self._sqlite:
                placeholder = '?'
            else:
                placeholder = '%s'
            
            values_str  = '(%s)' % string.joinfields((placeholder for col in table_format.cols), ', ')
            self._cmd   = 'INSERT INTO %s VALUES %s' % (self.table, values_str)
            
            count = 0
            for row in epf.parse_rows(f, table_format):
                self._parseRowOld(row, table_format)
                count += 1
                
                if numLines > 100 and (count % (numLines / 100)) == 0:
                    num_rows = self.execute('SELECT COUNT(*) FROM %s' % (self.table, )).fetchone()[0]
                    
                    utils.log("[%s] done parsing %s -- %d rows" % \
                        (self, utils.getStatusStr(count, numLines), num_rows))
            
            self._try_flush_buffer(force=True)
            
            if self.index:
                self.execute("CREATE INDEX %s on %s (%s)" % (self.index, self.table, self.index), verbose=True)
            
            utils.log("[%s] finished parsing %d rows" % (self, count))
        
        f.close()
        self._output.put(StopIteration)
    
    def _parseRowOld(self, row, table_format):
        ret  = { }
        cols = self.table_format.cols
        
        for col in cols:
            index = cols[col].index
            ret[col] = row[index]
        
        ret = AttributeDict(ret)
        return self._parseRow(ret, row)
    
    def _parseRow(self, row, row_list):
        #pprint(dict(row))
        #print row_list
        
        try:
            retain_result = self._filter(row)
        except ValueError:
            #utils.printException()
            # sometime malformed rows will cause problems with the filters. we 
            # want to ignore these rows anyway, so just ignore the error and 
            # filter this row out.
            retain_result = False
        
        if not retain_result:
            return
        
        for i in xrange(len(row_list)):
            if row_list[i] == '':
                row_list[i] = None
        
        self._buffer.append((row, row_list))
        self._try_flush_buffer()
    
    def _try_flush_buffer(self, force=False):
        if not force and len(self._buffer) < self._buffer_threshold:
            return
        
        for k in self._buffer:
            row, row_list = k
            
            if self._sqlite:
                try:
                    self.db.execute(self._cmd, row_list)
                except sqlite3.OperationalError, e:
                    utils.log(self._cmd)
                    
                    utils.log(row)
                    utils.log(row_list)
                    raise
            else:
                try:
                    self.db.execute(self._cmd, row_list)
                except psycopg2.Error, e:
                    utils.log(e.pgerror)
                    
                    utils.log(self._cmd)
                    utils.log(row)
                    utils.log(row_list)
                    
                    self.conn.rollback()
                    raise
        
        """
        try:
            self.db.executemany(self._cmd, self._buffer)
        except psycopg2.Error, e:
            utils.log(e.pgerror)
            utils.log(self._cmd)
            self.conn.rollback()
            raise
        """
        
        self._buffer = []
        self.conn.commit()

class AppleEPFArtistRelationalDB(AppleEPFRelationalDB):
    
    _blacklist_characters = set([
        '/', 
        ';', 
        ',', 
        '&', 
    ])
    
    _blacklist_strings = [
        'ft.',  
        'Ft.',  
        'feat.',  
        'Feat.',  
        'feat',  
        'Feat',  
        'featuring',  
        'Featuring',  
        '.com',  
        ' present ',  
        ' Present ',  
        ' and ', # TODO: will this produce too many false positives?
        'attributed', 
        'Attributed', 
        'Tribute', 
        'tribute ', 
        'tributes ', 
        'niversity', 
        'Ringtones', 
        'araoke', 
    ]
    
    _blacklist_suffixes = [
        ' instrumental'
    ]
    
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Artists", 
                                      filename="artist", 
                                      index="artist_id")
    
    def _filter(self, row):
        artist_type = AppleEPFArtistTypeDB()
        artist_type.start()
        
        self.artist_to_albums = AppleEPFArtistsToAlbumsRelationalDB()
        self.artist_to_albums.start()
        
        self.artist_to_songs = AppleEPFArtistsToSongsRelationalDB()
        self.artist_to_songs.start()
        
        self.album_popularity_per_genre = AppleEPFAlbumPopularityPerGenreRelationalDB()
        self.album_popularity_per_genre.start()
        
        self.song_popularity_per_genre = AppleEPFSongPopularityPerGenreRelationalDB()
        self.song_popularity_per_genre.start()
        
        self.genres = AppleEPFGenreRelationalDB()
        self.genres.start()
        
        artist_type.join()
        self.artist_to_albums.join()
        self.artist_to_songs.join()
        self.album_popularity_per_genre.join()
        self.song_popularity_per_genre.join()
        self.genres.join()
        
        self.artist_type_id = int(artist_type.get_row('name', 'Artist')['artist_type_id'])
        artist_type_id   = int(row.artist_type_id)
        is_actual_artist = int(row.is_actual_artist)
        
        """
        Blacklist:
            tribute bands
            
            feat: 
                Miri Ben Ari feat. Joe Budden & Mr. Maygreen
                Yusef, Malik Feat. Kanye West
                Kanye West featuring Lupe Fiasco
                Pharrell feat Kanye West
                LOVESCANDAL/ feat TINA
                Kanye West ft. Fonzworth Bentley & Twista
                Kanye West  Featuring Dwele
            
             multiple artists:
                Kanye West; John Stephens; Dexter Mills
                Cyssero / Kanye West / Neyo
                David Bennent, Georg Nigl, Franck Ollu, Ensemble Modern, Deutscher Kammerchor
                Kanye West,Milton Mascimento,Dexter Mills
                Kanye West and Deric"D-Dot"Angelettie
                Maelstrom aka DJ Emok & NDSA
                Malik Yusef, Kanye West & Adam Levine
                Xen Nightz & Kanye West
                K.Goss/K.Rhodes/B.N.Chapman
                Revil/Lemarque/Turner/Parsons
            
            misc:
                University of Texas Wind Ensemble
                The Len Browsn Society
                ReachMyFile.com
                P. Diddy for Bad Boy Entertainment, Inc.
                V\xc3\xa1radi Roma Caf\xc3\xa9
                L\xc3\xa1szl\xc3\xb3 Kom\xc3\xa1r
                Zolt\xc3\xa1n Cs\xc3\xa1nyi
                Lindstr\xc3\xb8m
                K\xc3\xa5re Korneliussen
                present Karla Brown
                Dino and Terry Present Karla Brown
                \xe3\x83\xa9\xe3\x82\xa6\xe3\x83\xa9\xe3\x83\xbb\xe3\x82\xa2\xe3\x83\xab\xe3\x83\x93\xe3\x83\xbc\xe3\x83\x8e
                M\xc3\xa9lodie Zhao
                W,O,W,Machine
                Fain \xc2\x96 Brown
                Edgar Froese \xc2\x96 Jerome Froese
                H\xc3\xbclya S\xc3\xbcer
                \xe4\xba\x95\xe4\xb8\x8a \xe3\x81\x8b\xe3\x81\xa4\xe3\x81\x8a
                remove anything that appears in ALL CAPS
        
        Transformations:
            BORIS P. BRANSBY WILLIAMS => Boris P. Bransby Williams
        
        Whitelist:
            24/8
            Mookie Knobbs and the Agitators
        """
        
        if not is_actual_artist or artist_type_id != self.artist_type_id:
            return False
        
        name = row.name
        
        for letter in name:
            # only accept primary ascii characters
            if letter in self._blacklist_characters or letter < ' ' or letter > 'z':
                return False
        
        for s in self._blacklist_strings:
            if s in name:
                return False
        
        for s in self._blacklist_suffixes:
            if name.endswith(s):
                return False
        
        return True

class AppleEPFSongRelationalDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Songs", 
                                      filename="song", 
                                      index="song_id")
    
    def _filter(self, row):
        if row.name is None or len(row.name) <= 0:
            return False
        
        try:
            # ensure that invalid rows are filtered out
            song_id = int(row.song_id)
        except ValueError:
            return False
        
        return True

class AppleEPFAlbumRelationalDB(AppleEPFRelationalDB):
    
    _blacklist_strings = [
        'araoke', 
        '- Single', 
        '- single', 
    ]
    
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Albums", 
                                      filename="collection", 
                                      index="collection_id")
        
        collection_type = AppleEPFCollectionTypeDB()
        collection_type.start()
        
        media_type = AppleEPFMediaTypeDB()
        media_type.start()
        
        self.album_prices = AppleEPFAlbumPriceRelationalDB()
        self.album_prices.start()
        
        collection_type.join()
        media_type.join()
        self.album_prices.join()
        
        self.album_type_id = int(collection_type.get_row('name', 'Album')['collection_type_id'])
        self.music_type_id = int(media_type.get_row('name', 'Music')['media_type_id'])
    
    def _filter(self, row):
        collection_type_id = int(row.collection_type_id)
        
        # only retain album collections
        if collection_type_id != self.album_type_id:
            return False
        
        media_type_id = int(row.media_type_id)
        
        # only retain music collections
        if media_type_id != self.music_type_id:
            return False
        
        name = row.name
        for s in self._blacklist_strings:
            if s in name:
                return False
        
        return True
        collection_id = int(row.collection_id)
        
        # only retain albums which are available for purchase in the US storefront
        price_info = self.album_prices.get_row('collection_id', collection_id)
        
        if price_info is None:
            return False
        
        return True

class AppleEPFVideoDump(AppleEPFRelationalDB):
    
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Videos", 
                                      filename="video", 
                                      index="video_id")
        
        media_type = AppleEPFMediaTypeDB()
        media_type.start()
        
        self.video_prices = AppleEPFVideoPriceRelationalDB()
        self.video_prices.start()
        
        media_type.join()
        self.video_prices.join()
        
        self.movie_type_id = int(media_type.get_row('name', 'Movies')['media_type_id'])
    
    def _filter(self, row):
        media_type_id = int(row.media_type_id)
        
        # only keep videos which are movies
        if media_type_id != self.movie_type_id:
            return False
        
        video_id = (row.video_id)
        
        # only retain videos which are available for purchase in the US storefront
        price_info = self.video_prices.get_row('video_id', video_id)
        
        if price_info is None:
            return False
        
        return True

class AppleEPFCollectionTypeDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Collection Types", 
                                      filename="collection_type", 
                                      index="collection_type_id")

class AppleEPFArtistTypeDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Artist Types", 
                                      filename="artist_type", 
                                      index="artist_type_id")

class AppleEPFMediaTypeDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Media Types", 
                                      filename="media_type", 
                                      index="media_type_id")

class AppleEPFGenreRelationalDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Genres", "genre")

class AppleEPFVideoPriceRelationalDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Video Prices", 
                                      filename="video_price", 
                                      index="video_id")
        
        g = AppleEPFStorefrontDB()
        g.start()
        g.join()
        self.us_storefront_id = g.get_row('country_code', 'USA')['storefront_id']
    
    def _filter(self, row):
        storefront_id = int(row.storefront_id)
        
        # only retain us prices
        return storefront_id == self.us_storefront_id

class AppleEPFAlbumPriceRelationalDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Album Prices", 
                                      filename="collection_price", 
                                      index="collection_id")
        
        g = AppleEPFStorefrontDB()
        g.start()
        g.join()
        self.us_storefront_id = g.get_row('country_code', 'USA')['storefront_id']
    
    def _filter(self, row):
        storefront_id = int(row.storefront_id)
        
        # only retain us prices
        return storefront_id == self.us_storefront_id

class AppleEPFStorefrontDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Storefronts", 
                                      filename="storefront")

class AppleEPFRoleDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Artist Roles", 
                                      filename="role")

class AppleEPFArtistsToAlbumsRelationalDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Artists to Albums", 
                                      filename="artist_collection", 
                                      index="artist_id")
        
        g = AppleEPFRoleDB()
        g.start()
        g.join()
        
        self.role_ids = set([
            #g.get_row('name', 'Author')['role_id'], 
            #g.get_row('name', 'Composer')['role_id'], 
            #g.get_row('name', 'ComposerAuthor')['role_id'], 
            g.get_row('name', 'Performer')['role_id'], 
        ])
    
    def _filter(self, row):
        #pprint(row)
        #is_primary_artist = int(row.is_primary_artist)
        #if not is_primary_artist:
        #    return False
        
        #role_id = int(row.role_id)
        #if role_id not in self.role_ids:
        #    return False
        
        return True

class AppleEPFArtistsToSongsRelationalDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Artists to Songs", 
                                      filename="artist_song", 
                                      index="artist_id")

class AppleEPFAlbumPopularityPerGenreRelationalDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Album Popularity per Genre", 
                                      filename="album_popularity_per_genre", 
                                      index="album_id")
        
        g = AppleEPFStorefrontDB()
        g.start()
        g.join()
        self.us_storefront_id = g.get_row('country_code', 'USA')['storefront_id']
    
    def _filter(self, row):
        storefront_id = int(row.storefront_id)
        
        # only retain us popularity metrics
        return storefront_id == self.us_storefront_id

class AppleEPFSongPopularityPerGenreRelationalDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Song Popularity per Genre", 
                                      filename="song_popularity_per_genre", 
                                      index="song_id")
        
        g = AppleEPFStorefrontDB()
        g.start()
        g.join()
        self.us_storefront_id = g.get_row('country_code', 'USA')['storefront_id']
    
    def _filter(self, row):
        storefront_id = int(row.storefront_id)
        
        # only retain us popularity metrics
        return storefront_id == self.us_storefront_id

class AppleEPFAlbumToSongDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Album to Song", 
                                      filename="collection_song", 
                                      index="collection_id")

