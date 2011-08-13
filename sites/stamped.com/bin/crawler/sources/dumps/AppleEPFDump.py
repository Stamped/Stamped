#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import CSVUtils, epf, gevent, gzip, os, re, sqlite3, string, time, urllib

from gevent.pool import Pool
from utils import lazyProperty, Singleton
from AEntitySource import AExternalDumpEntitySource
from ASyncGatherSource import ASyncGatherSource
from api.Entity import Entity

from boto.ec2.connection import EC2Connection
from boto.exception import EC2ResponseError
from errors import Fail

__all__ = [ "AppleEPFDump" ]

APPLE_EPF_USER = "St4mp3d"
APPLE_EPF_PSWD = "f16b8ea6534b1970c466a71c41fa9c9c"

AWS_ACCESS_KEY_ID = 'AKIAIXLZZZT4DMTKZBDQ'
AWS_SECRET_KEY = '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'

class AppleEPFOpener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return (APPLE_EPF_USER, APPLE_EPF_PSWD)

class AppleEPFDistro(Singleton):
    @lazyProperty
    def apple_data_dir(self):
        if self.ec2:
            self._volume = 'vol-52db3938'
            #'vol-80ba5bea'
            
            self._instance_id = utils.shell('wget -q -O - http://169.254.169.254/latest/meta-data/instance-id')[0]
            
            self.conn = EC2Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY)
            volume_dir = "/dev/sdh5"
            mount_dir  = "/mnt/crawlerdata"
            
            if not Globals.options.mount:
                while not os.path.exists(mount_dir):
                    time.sleep(5)
            else:
                volume = self.conn.get_all_volumes(volume_ids=[self._volume])[0]
                
                if volume.status != 'in-use' or volume.attach_data.instance_id != self._instance_id or volume.attach_data.device != volume_dir:
                    utils.shell("sudo mkdir -p %s" % mount_dir)
                    
                    if volume.status != 'available':
                        try:
                            utils.log("unmounting and detaching volume '%s' from '%s'" % (self._volume, volume_dir))
                            utils.shell('umount %s' % volume_dir)
                            volume.detach(force=True)
                        except EC2ResponseError:
                            pass
                        time.sleep(6)
                        while volume.status != 'available':
                            time.sleep(2)
                            print volume.update()
                    
                    utils.log("apple data volume '%s' on instance '%s': attaching at '%s' and mounting at '%s'" % (self._volume, self._instance_id, volume_dir, mount_dir))
                    try:
                        ret = self.conn.attach_volume(self._volume, self._instance_id, volume_dir)
                        assert ret
                    except EC2ResponseError:
                        utils.log("unable to mount apple data volume '%s' on instance '%s'" % (self._volume, self._instance_id))
                        raise
                    
                    while volume.status != u'in-use':
                        time.sleep(2)
                        volume.update()
                    
                    time.sleep(4)
                    
                    while not os.path.exists(mount_dir):
                        time.sleep(2)
                    
                    mounted = False
                    while not mounted:
                        mounted = 0 == utils.shell('mount -t ext3 %s %s' % (volume_dir, mount_dir))[1]
                        time.sleep(3)
            
            return mount_dir
        else:
            base = os.path.dirname(os.path.abspath(__file__))
            
            apple_dir = os.path.join(os.path.join(base, "data"), "apple")
            assert os.path.exists(apple_dir)
            return apple_dir
    
    def cleanup(self):
        if self.ec2:
            # unmount and detach volume
            sudo("umount %s" % self.apple_data_dir)
            # TODO: detach volume
            #volume.detach()
    
    @lazyProperty
    def ec2(self):
        if not os.path.exists("/proc/xen"):
            return False
        if os.path.exists("/etc/ec2_version"):
            return True
        
        return False

class AppleEPFDumps(ASyncGatherSource):
    """
        Importer from Apple EPF Feed
    """
    
    NAME = "Apple EPF Importer"
    TYPES = set([ 'iPhoneApp' ])
    
    def __init__(self):
        # TODO: deal with types not getting passed correctly to AEntitySource
        sources = [
            AppleEPFArtistDump(self), 
        ]
        
        self._pool = Pool(512)
        ASyncGatherSource.__init__(self, sources)
        self.init()
    
    def init(self):
        baseurl = "http://feeds.itunes.apple.com/feeds/epf/v3/full/current"
        
        opener = AppleEPFOpener()
        soup = utils.getSoup(baseurl, opener.open)
        opener.close()
        
        links = soup.findAll('a', {'href' : re.compile(r"[^.]*.tbz$")})
        assert len(links) == 4
        
        utils.shell("mkdir -p %s" % self.apple_data_dir)
        
        for link in links:
            suffix = link.get("href")
            #self._init_feed('%s/%s' % (baseurl, suffix), suffix)
            self._pool.spawn(self._init_feed, '%s/%s' % (baseurl, suffix), suffix)
        
        self._pool.join()
    
    def _init_feed(self, url, suffix):
        utils.log(url)
        utils.log(suffix)
        output = os.path.join(self.apple_data_dir, suffix)
        
        cmd = "curl --user %s:%s %s -o %s" % (APPLE_EPF_USER, APPLE_EPF_PSWD, url, output)
        utils.log(cmd)
        utils.shell(cmd)
        
        # TODO: use python tar utility to not extract anything!
        cmd = "cd %s && tar -xvf %s" % (self.apple_data_dir, suffix)
        utils.log(cmd)
        utils.shell(cmd)
        
        unpacked = suffix[:-4]
        cmd = "cd %s && mkdir -p archive && mv %s archive && mv -f %s/* ./" % (self.apple_data_dir, suffix, unpacked)
        utils.log(cmd)
        utils.shell(cmd)
    
    def getMaxNumEntities(self):
        raise NotImplementedError
    
    def _run(self):
        pass

class AAppleEPFDump(AExternalDumpEntitySource):
    
    def __init__(self, name, entityMap, types, filename):
        AExternalDumpEntitySource.__init__(self, name, types, 512)
        self._filename  = filename
        self._columnMap = entityMap
        
        self._distro = AppleEPFDistro.getInstance()
    
    def _open_file(self):
        filename = os.path.join(self._distro.apple_data_dir, self._filename)
        zipped = filename + ".gz"
        
        if not os.path.exists(filename) and not os.path.exists(zipped):
            if Globals.options.mount:
                raise Fail("ERROR: mount failed!")
            else:
                while (not os.path.exists(filename)) and (not os.path.exists(zipped)):
                    utils.log("waiting for mount to complete for file '%s'" % filename)
                    time.sleep(4)
        
        if os.path.exists(zipped):
            filename = zipped
        
        utils.log("Opening Apple EPF file '%s'" % filename)
        if not os.path.exists(filename):
            utils.log("Apple EPF file '%s' does not exist!" % filename)
            raise Fail("Apple EPF file '%s' does not exist!" % filename)
        
        if filename.endswith(".gz"):
            f = gzip.open(filename, 'rb')
        else:
            f = open(filename, 'r+b')
        
        numLines = max(0, CSVUtils.getNumLines(f) - 8)
        return f, numLines, filename
    
    def getMaxNumEntities(self):
        f, numLines, filename = self._open_file()
        f.close()
        
        return numLines
    
    def _run(self):
        utils.log("[%s] initializing" % self)
        f, numLines, filename = self._open_file()
        utils.log("[%s] parsing ~%d entities from '%s'" % (self, numLines, self._filename))
        
        table_format = epf.parse_table_format(f, filename)
        pool   = Pool(512)
        count  = 0
        offset = 0
        self.numFiltered = 0
        #self.filtered = []
        
        for row in epf.parse_rows(f, table_format):
            if offset < Globals.options.offset:
                offset += 1
                continue
            
            if Globals.options.limit and count >= Globals.options.limit:
                break
            
            pool.spawn(self._parseRow, row, table_format)
            count += 1
            
            if numLines > 100 and (count % (numLines / 100)) == 0:
                utils.log("[%s] done parsing %s" % \
                    (self, utils.getStatusStr(count, numLines)))
                time.sleep(0.1)
        
        pool.join()
        f.close()
        self._output.put(StopIteration)
        
        utils.log("[%s] finished parsing %d entities (filtered %d)" % (self, count, self.numFiltered))
        #for n in self.filtered:
        #    utils.log("FILTERED: %s" % n)
    
    def _parseRow(self, row, table_format):
        try:
            retain_result = self._filter(row, table_format)
        except ValueError:
            #utils.printException()
            # sometime malformed rows will cause problems with the filters. we 
            # want to ignore these rows anyway, so just ignore the error and 
            # filter this row out.
            retain_result = False
        
        if not retain_result:
            self.numFiltered += 1
            #self.filtered.append(row[table_format.cols.name.index])
            return
        
        entity = Entity()
        entity.subcategory = self.subcategories[0]
        
        # TODO: extract albums
        entity.albums = []
        
        if isinstance(retain_result, dict):
            for col, value in retain_result.iteritems():
                if value is not None:
                    entity[col] = value
        
        for col in table_format.cols:
            if col in self._columnMap:
                col2 = self._columnMap[col]
                if col2 is None:
                    continue
                
                index = table_format.cols[col]['index']
            
            value = row[index]
            #from pprint import pprint
            #print "%d) %s" % (index, table_format.cols)
            #pprint(row)
            
            entity[col2] = value
        
        self._output.put(entity)
    
    def _filter(self, row, table_format):
        return True

class AppleEPFArtistDump(AAppleEPFDump):
    
    _map = {
        'name'              : 'title', 
        'export_date'       : 'export_date', 
        'artist_id'         : 'aid', 
        'is_actual_artist'  : None, 
        'view_url'          : 'view_url', 
        'artist_type_id'    : None, 
    }
    
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
        AAppleEPFDump.__init__(self, "Apple EPF Artists", self._map, [ "artist" ], "artist")
        
        artist_type = AppleEPFArtistType()
        artist_type.start()
        
        self.artist_to_albums = AppleEPFArtistsToAlbumsRelationalDB()
        self.artist_to_albums.start()
        
        #self.artist_to_songs = AppleEPFArtistsToSongsRelationalDB()
        #self.artist_to_songs.start()
        
        self.album_popularity_per_genre = AppleEPFAlbumPopularityPerGenreRelationalDB()
        self.album_popularity_per_genre.start()
        
        #self.song_popularity_per_genre = AppleEPFSongPopularityPerGenreRelationalDB()
        #self.song_popularity_per_genre.start()
        
        self.genres = AppleEPFGenreRelationalDB()
        self.genres.start()
        
        artist_type.join()
        self.artist_to_albums.join()
        #self.artist_to_songs.join()
        self.album_popularity_per_genre.join()
        #self.song_popularity_per_genre.join()
        self.genres.join()
        
        self.artist_type_id = int(artist_type.results['Artist'])
    
    def _filter(self, row, table_format):
        artist_type_id = int(row[table_format.cols.artist_type_id.index])
        is_actual_artist = row[table_format.cols.is_actual_artist.index]
        
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
        
        name = row[table_format.cols.name.index]
        
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
        
        artist_id = int(row[table_format.cols.artist_id.index])
        
        # query for all albums by this artist
        albums = self.artist_to_albums.get_rows('artist_id', artist_id)
        
        if len(albums) <= 0:
            return False
        
        out_albums = []
        popularity = None
        
        for album in albums:
            album_id = album['collection_id']
            pop = self.album_popularity_per_genre.get_row('album_id', album_id)
            
            out_album = {
                'album_id' : album_id, 
            }
            
            if pop is not None:
                rank = pop['album_rank']
                
                if popularity is None or rank < popularity:
                    popularity = rank
                
                out_album['rank']     = rank
                out_album['genre_id'] = pop['genre_id']
            
            out_albums.append(out_album)
        
        # query for all songs by this artist
        """
        songs = self.artist_to_songs.get_rows('artist_id', artist_id)
        
        if len(songs) <= 0:
            return False
        
        for song in songs:
            song_id = song['song_id']
            pop = self.song_popularity_per_genre.get_row('song_id', song_id)
            
            if pop is not None:
                popular = True
        
        return popular
        """
        
        return {
            'albums' : out_albums, 
            'popularity' : popularity, 
        }

class AppleEPFSongDump(AAppleEPFDump):
    
    _map = {
        'name'                      : 'title', 
        'export_date'               : 'export_date', 
        'song_id'                   : 'aid', 
        'title_version'             : 'title_version', 
        'search_terms'              : 'search_terms', 
        'parental_advisory_id'      : 'parental_advisory_id', 
        'artist_display_name'       : 'artist_display_name', 
        'collection_display_name'   : 'collection_display_name', 
        'view_url'                  : 'view_url', 
        'original_release_date'     : 'original_release_date', 
        'itunes_release_date'       : 'itunes_release_date', 
        'track_length'              : 'track_length', 
        'copyright'                 : 'copyright', 
        'p_line'                    : 'p_line', 
        'preview_url'               : 'preview_url', 
        'preview_length'            : 'preview_length', 
    }
    
    def __init__(self):
        AAppleEPFDump.__init__(self, "Apple EPF Songs", self._map, [ "song" ], "song")

class AppleEPFAlbumDump(AAppleEPFDump):
    
    _map = {
        'name'                      : 'title', 
        'export_date'               : 'export_date', 
        'collection_id'             : 'aid', 
        'title_version'             : 'title_version', 
        'search_terms'              : 'search_terms', 
        'parental_advisory_id'      : 'parental_advisory_id', 
        'artist_display_name'       : 'artist_display_name', 
        'view_url'                  : 'view_url', 
        'artwork_url'               : 'artwork_url', 
        'original_release_date'     : 'original_release_date', 
        'itunes_release_date'       : 'itunes_release_date', 
        'label_studio'              : 'label_studio', 
        'content_provider_name'     : 'content_provider_name', 
        'copyright'                 : 'copyright', 
        'p_line'                    : 'p_line', 
        'media_type_id'             : 'media_type_id', 
        'is_compilation'            : 'is_compilation', 
        'collection_type_id'        : None, 
    }
    
    def __init__(self):
        AAppleEPFDump.__init__(self, "Apple EPF Albums", self._map, [ "album" ], "collection")
        
        collection_type = AppleEPFCollectionType()
        collection_type.start()
        
        self.album_prices = AppleEPFAlbumPriceRelationalDB()
        self.album_prices.start()
        
        collection_type.join()
        self.album_prices.join()
        
        self.album_type_id = int(collection_type.results['Album'])
    
    def _filter(self, row, table_format):
        collection_type_id = int(row[table_format.cols.collection_type_id.index])
        
        # only retain album collections
        if collection_type_id != self.album_type_id:
            #print "%s (%s) vs %s (%s)" % (collection_type_id, type(collection_type_id), self.album_type_id, type(self.album_type_id))
            
            return False
        
        artist_display_name = row[table_format.cols.artist_display_name.index]
        if len(artist_display_name) <= 0:
            return False
        
        collection_id = int(row[table_format.cols.collection_id.index])
        
        # only keep albums which are available for purchase in the US storefront
        price_info = self.album_prices.get_row('collection_id', collection_id)
        
        if price_info is None:
            return False
        
        return {
            'a_retail_price' : price_info['retail_price'], 
            'a_hq_price' : price_info['hq_price'], 
            'a_currency_code' : price_info['currency_code'], 
            'a_availability_date' : price_info['availability_date'], 
        }

class AppleEPFVideoDump(AAppleEPFDump):
    
    _map = {
        'name'                      : 'title', 
        'export_date'               : 'export_date', 
        'video_id'                  : 'aid', 
        'title_version'             : 'title_version', 
        'search_terms'              : 'search_terms', 
        'parental_advisory_id'      : 'parental_advisory_id', 
        'artist_display_name'       : 'artist_display_name', 
        'collection_display_name'   : 'collection_display_name', 
        'view_url'                  : 'view_url', 
        'artwork_url'               : 'artwork_url', 
        'original_release_date'     : 'original_release_date', 
        'itunes_release_date'       : 'itunes_release_date', 
        'studio_name'               : 'studio_name', 
        'network_name'              : 'network_name', 
        'content_provider_name'     : 'content_provider_name', 
        'track_length'              : 'track_length', 
        'copyright'                 : 'copyright', 
        'p_line'                    : 'p_line', 
        'short_description'         : 'short_description', 
        'episode_production_number' : 'episode_production_number', 
        'media_type_id'             : None, 
    }
    
    def __init__(self):
        AAppleEPFDump.__init__(self, "Apple EPF Videos", self._map, [ "movie" ], "video")
        
        media_type = AppleEPFMediaType()
        media_type.start()
        
        self.video_prices = AppleEPFVideoPriceRelationalDB()
        self.video_prices.start()
        
        media_type.join()
        self.video_prices.join()
        
        self.movie_type_id = int(media_type.results['Movies'])
    
    def _filter(self, row, table_format):
        media_type_id = int(row[table_format.cols.media_type_id.index])
        
        # only keep videos which are movies
        if media_type_id != self.movie_type_id:
            return False
        
        video_id = int(row[table_format.cols.video_id.index])
        
        # only keep videos which are available for purchase in the US storefront
        price_info = self.video_prices.get_row('video_id', video_id)
        
        if price_info is None:
            return False
        
        return {
            'v_retail_price' : price_info['retail_price'], 
            'v_currency_code' : price_info['currency_code'], 
            'v_availability_date' : price_info['availability_date'], 
            'v_sd_price' : price_info['sd_price'], 
            'v_hq_price' : price_info['hq_price'], 
            'v_lc_rental_price' : price_info['lc_rental_price'], 
            'v_sd_rental_price' : price_info['sd_rental_price'], 
            'v_hd_rental_price' : price_info['hd_rental_price'], 
        }

class AppleEPFCollectionType(AAppleEPFDump):
    def __init__(self):
        AAppleEPFDump.__init__(self, "Apple EPF Collection Types", None, [ ], "collection_type")
        self.results = { }
    
    def _parseRow(self, row, table_format):
        name = row[table_format.cols.name.index]
        self.results[name] = int(row[table_format.cols.collection_type_id.index])

class AppleEPFArtistType(AAppleEPFDump):
    def __init__(self):
        AAppleEPFDump.__init__(self, "Apple EPF Artist Types", None, [ ], "artist_type")
        self.results = { }
    
    def _parseRow(self, row, table_format):
        name = row[table_format.cols.name.index]
        self.results[name] = int(row[table_format.cols.artist_type_id.index])

class AppleEPFMediaType(AAppleEPFDump):
    def __init__(self):
        AAppleEPFDump.__init__(self, "Apple EPF Media Types", None, [ ], "media_type")
        self.results = { }
    
    def _parseRow(self, row, table_format):
        name = row[table_format.cols.name.index]
        self.results[name] = int(row[table_format.cols.media_type_id.index])

class AppleEPFRelationalDB(AAppleEPFDump):
    def __init__(self, name, filename, index=None):
        AAppleEPFDump.__init__(self, name, None, [ ], filename)
        self.index = index
        self._init_sqlite3(filename)
    
    def _init_sqlite3(self, filename):
        # initialize sqlite connection
        self.dbpath = "%s.db" % filename
        self.table  = "stamped"
        #self.dbpath = "apple_epf.db"
        #self.table  = filename
        self.conn   = sqlite3.connect(self.dbpath)
        self.db     = self.conn.cursor()
    
    def close(self):
        if self.db is not None:
            self.db.close()
            self.db = None
    
    def execute(self, cmd, verbose=False, error_okay=False):
        if verbose:
            utils.log(cmd)
        
        try:
            return self.db.execute(cmd)
        except sqlite3.OperationalError:
            if not error_okay:
                utils.log('warning: error running sqlite cmd "%s"' % (cmd, ))
                raise
    
    def _run(self):
        utils.log("[%s] initializing" % self)
        f, numLines, filename = self._open_file()
        
        table_format = epf.parse_table_format(f, filename)
        self.table_format = table_format
        
        stale = False
        self._buffer = []
        self._buffer_threshold = 1024
        
        # determine whether or not the sqlite table already exists and attempt 
        # to determine if it's up-to-date s.t. we won't recalculate it if it'd 
        # be unnecessary.
        try:
            row0  = self.execute('SELECT * FROM %s' % (self.table, ), error_okay=True).fetchone()
            count = self.execute('SELECT COUNT(*) FROM %s' % (self.table, ), error_okay=True).fetchone()[0]
            
            if row0 is None or count is None:
                stale = True
            elif len(row0) != len(dict(table_format.cols)):
                stale = True
        except Exception:
            #utils.printException()
            stale = True
            pass
        
        if not stale:
            # sqlite table is usable as-is
            utils.log("[%s] %s.%s doesn't need to be recomputed" % (self, self.dbpath, self.table))
        else:
            utils.log("[%s] parsing ~%d rows from '%s'" % (self, numLines, self._filename))
            # initialize sqlite table
            cols = []
            
            # currently disabling primary keys for most tables
            found_primary = (len(table_format.primary_keys) == 1)
            
            for col in table_format.cols:
                cols.append('')
            
            for col in table_format.cols:
                primary = ""
                if not found_primary and col in table_format.primary_keys:
                    # TODO: handle the common case of multiple primary keys, which sqlite3 does not support
                    # TODO: defining the primary key here as opposed to after insertion is much slower!
                    primary = " PRIMARY KEY"
                    found_primary = True
                
                col2 = table_format.cols[col]
                col_type = col2['type']
                text = "%s %s%s" % (col, col_type, primary)
                index = col2['index']
                cols[index] = text
            
            args = string.joinfields(cols, ', ')
            try:
                self.execute("DROP TABLE %s" % (self.table, ), error_okay=True)
            except sqlite3.OperationalError:
                pass
            
            self.execute("CREATE TABLE %s (%s)" % (self.table, args), verbose=True)
            
            values_str = '(%s)' % (string.joinfields(('?' for col in table_format.cols), ','), )
            self._cmd = 'INSERT INTO %s VALUES %s' % (self.table, values_str)
            
            count = 0
            for row in epf.parse_rows(f, table_format):
                self._parseRow(row, table_format)
                count += 1
                
                if numLines > 100 and (count % (numLines / 100)) == 0:
                    utils.log("[%s] done parsing %s" % \
                        (self, utils.getStatusStr(count, numLines)))
            
            self._try_flush_buffer()
            
            if self.index:
                self.execute("CREATE INDEX %s on %s (%s)" % (self.index, self.table, self.index), verbose=True)
            
            utils.log("[%s] finished parsing %d rows" % (self, count))
        
        f.close()
        self._output.put(StopIteration)
    
    def _parseRow(self, row, table_format):
        try:
            retain_result = self._filter(row, table_format)
        except ValueError:
            #utils.printException()
            # sometime malformed rows will cause problems with the filters. we 
            # want to ignore these rows anyway, so just ignore the error and 
            # filter this row out.
            retain_result = False
        
        if not retain_result:
            return
        
        self._buffer.append(tuple(row))
        self._try_flush_buffer()
    
    def _try_flush_buffer(self):
        if len(self._buffer) < self._buffer_threshold:
            return
        
        # TODO: use self.db.execute_many
        for row in self._buffer:
            self.db.execute(self._cmd, row)
        
        self.conn.commit()
        self._buffer = []
    
    def _get_cmd_results(self, k, v):
        if isinstance(v, basestring):
            v = "'%s'" % v
        
        cmd = 'SELECT * from %s where %s=%s' % (self.table, k, v)
        return self.execute(cmd)
    
    def _format_result(self, result):
        if result is not None:
            ret = { }
            cols = self.table_format.cols
            for col in cols:
                index = cols[col].index
                ret[col] = result[index]
            
            result = ret
        
        return result
    
    def get_row(self, k, v):
        result = self._get_cmd_results(k, v).fetchone()
        
        return self._format_result(result)
    
    def get_rows(self, k, v):
        results = self._get_cmd_results(k, v).fetchmany()
        
        if results is None:
            return []
        for i in xrange(len(results)):
            results[i] = self._format_result(results[i])
        
        return results

class AppleEPFGenreRelationalDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Genres", "genre")

class AppleEPFVideoPriceRelationalDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Video Prices", 
                                      filename="video_price", 
                                      index="video_id")
        
        g = AppleEPFStorefrontDump()
        g.start()
        g.join()
        self.us_storefront_id = g.get_row('country_code', 'USA')['storefront_id']
    
    def _filter(self, row, table_format):
        storefront_id = int(row[table_format.cols.storefront_id.index])
        
        # only retain us prices
        return storefront_id == self.us_storefront_id

class AppleEPFAlbumPriceRelationalDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Album Prices", 
                                      filename="collection_price", 
                                      index="collection_id")
        
        g = AppleEPFStorefrontDump()
        g.start()
        g.join()
        self.us_storefront_id = g.get_row('country_code', 'USA')['storefront_id']
    
    def _filter(self, row, table_format):
        storefront_id = int(row[table_format.cols.storefront_id.index])
        
        # only retain us prices
        return storefront_id == self.us_storefront_id

class AppleEPFStorefrontDump(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Storefronts", 
                                      filename="storefront")

class AppleEPFRoleDump(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Artist Roles", 
                                      filename="role")

class AppleEPFArtistsToAlbumsRelationalDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Artists to Albums", 
                                      filename="artist_collection", 
                                      index="artist_id")
        
        g = AppleEPFRoleDump()
        g.start()
        g.join()
        
        self.role_ids = set([
            #g.get_row('name', 'Author')['role_id'], 
            #g.get_row('name', 'Composer')['role_id'], 
            #g.get_row('name', 'ComposerAuthor')['role_id'], 
            g.get_row('name', 'Performer')['role_id'], 
        ])
    
    def _filter(self, row, table_format):
        is_primary_artist = row[table_format.cols.is_primary_artist.index]
        if not is_primary_artist:
            return False
        
        role_id = int(row[table_format.cols.role_id.index])
        if role_id not in self.role_ids:
            return False
        
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
        
        g = AppleEPFStorefrontDump()
        g.start()
        g.join()
        self.us_storefront_id = g.get_row('country_code', 'USA')['storefront_id']
    
    def _filter(self, row, table_format):
        storefront_id = int(row[table_format.cols.storefront_id.index])
        
        # only retain us popularity metrics
        return storefront_id == self.us_storefront_id

class AppleEPFSongPopularityPerGenreRelationalDB(AppleEPFRelationalDB):
    def __init__(self):
        AppleEPFRelationalDB.__init__(self, "Apple EPF Song Popularity per Genre", 
                                      filename="song_popularity_per_genre", 
                                      index="song_id")
        
        g = AppleEPFStorefrontDump()
        g.start()
        g.join()
        self.us_storefront_id = g.get_row('country_code', 'USA')['storefront_id']
    
    def _filter(self, row, table_format):
        storefront_id = int(row[table_format.cols.storefront_id.index])
        
        # only retain us popularity metrics
        return storefront_id == self.us_storefront_id

import EntitySources

#EntitySources.registerSource('apple', AppleEPFDumps)
EntitySources.registerSource('apple_artists', AppleEPFArtistDump)
#EntitySources.registerSource('apple_songs',   AppleEPFSongDump)
EntitySources.registerSource('apple_albums',  AppleEPFAlbumDump)
EntitySources.registerSource('apple_videos',  AppleEPFVideoDump)

