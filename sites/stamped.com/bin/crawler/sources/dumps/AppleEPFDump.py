#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import CSVUtils, epf, gevent, gzip, os, re, time, urllib

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
        utils.log("%s run" % self)
        f, numLines, filename = self._open_file()
        utils.log("[%s] parsing ~%d entities from '%s'" % (self, numLines, self._filename))
        
        table_format = epf.parse_table_format(f, filename)
        pool   = Pool(512)
        count  = 0
        offset = 0
        
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
        self._output.put(StopIteration)
        utils.log("[%s] finished parsing %d entities" % (self, count))
    
    def _parseRow(self, row, table_format):
        if not self._filter(row, table_format):
            return
        
        entity = Entity()
        entity.category = self._types[0]
        
        # TODO: extract albums
        entity.albums = []
        
        for col in table_format.cols:
            if col in self._columnMap:
                col2 = self._columnMap[col]
                index = table_format.cols[col]['index']
                
                if col2 is None:
                    continue
            
            value = row[index]
            #from pprint import pprint
            #print "%d) %s" % (index, table_format.cols)
            #pprint(row)
            
            # TODO: unsafe
            exec("entity.%s = value" % col2)
        
        self._output.put(entity)
    
    def _filter(self, row, table_format):
        return True

class AppleEPFArtistDump(AAppleEPFDump):
    
    _map = {
        'name'              : 'title', 
        'export_date'       : 'export_date', 
        'artist_id'         : 'aid', 
        'is_actual_artist'  : 'is_actual_artist', 
        'view_url'          : 'view_url', 
        'artist_type_id'    : None, 
    }
    
    def __init__(self):
        AAppleEPFDump.__init__(self, "Apple EPF Artists", self._map, [ "artist" ], "artist")
        
        g = AppleEPFArtistType()
        g.start()
        g.join()
        self.artist_type_id = g.results['Artist']
    
    def _filter(self, row, table_format):
        artist_type_id = row[table_format.cols.artist_type_id.index]
        
        # only retain song artists
        return artist_type_id == self.artist_type_id

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
        
        g = AppleEPFCollectionType.getInstance()
        g.start()
        g.join()
        self.album_type_id = g.results['Album']
    
    def _filter(self, row, table_format):
        collection_type_id = row[table_format.cols.collection_type_id.index]
        
        # only retain album collections
        return collection_type_id == self.album_type_id

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
        AAppleEPFDump.__init__(self, "Apple EPF Videos", self._map, [ "video" ], "video")
        
        g = AppleEPFMediaType()
        g.start()
        g.join()
        self.movie_type_id = g.results['Movies']
    
    def _filter(self, row, table_format):
        media_type_id = row[table_format.cols.media_type_id.index]
        return media_type_id == self.movie_type_id

class AppleEPFCollectionType(AAppleEPFDump):
    def __init__(self):
        AAppleEPFDump.__init__(self, "Apple EPF Collection Types", None, [ ], "collection_type")
        self.results = { }
    
    def _parseRow(self, row, table_format):
        name = row[table_format.cols.name.index]
        self.results[name] = row[table_format.cols.collection_type_id.index]

class AppleEPFArtistType(AAppleEPFDump):
    def __init__(self):
        AAppleEPFDump.__init__(self, "Apple EPF Artist Types", None, [ ], "artist_type")
        self.results = { }
    
    def _parseRow(self, row, table_format):
        name = row[table_format.cols.name.index]
        self.results[name] = row[table_format.cols.artist_type_id.index]

class AppleEPFMediaType(AAppleEPFDump):
    def __init__(self):
        AAppleEPFDump.__init__(self, "Apple EPF Media Types", None, [ ], "media_type")
        self.results = { }
    
    def _parseRow(self, row, table_format):
        name = row[table_format.cols.name.index]
        self.results[name] = row[table_format.cols.media_type_id.index]

class AppleEPFStorefrontDump(AAppleEPFDump):
    def __init__(self):
        AAppleEPFDump.__init__(self, "Apple EPF Storefronts", None, [ ], "storefront")
        self.results = { }
    
    def _parseRow(self, row, table_format):
        country_code = row[table_format.cols.country_code.index]
        self.results[country_code] = {
            'storefront_id' : row[table_format.cols.storefront_id.index], 
            'name' : row[table_format.cols.name.index], 
        }

import EntitySources

#EntitySources.registerSource('apple', AppleEPFDumps)
EntitySources.registerSource('apple_artists', AppleEPFArtistDump)
#EntitySources.registerSource('apple_songs',   AppleEPFSongDump)
EntitySources.registerSource('apple_albums',  AppleEPFAlbumDump)
EntitySources.registerSource('apple_videos',  AppleEPFVideoDump)

