#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import CSVUtils, epf, gevent, os, re, urllib

from gevent.pool import Pool
from AEntitySource import AExternalDumpEntitySource
from ASyncGatherSource import ASyncGatherSource
from api.Entity import Entity

__all__ = [ "AppleEPFDump" ]

APPLE_EPF_USER = "St4mp3d"
APPLE_EPF_PSWD = "f16b8ea6534b1970c466a71c41fa9c9c"

BASE = os.path.dirname(os.path.abspath(__file__))
APPLE_DATA_DIR = os.path.join(os.path.join(BASE, "data"), "apple")

class AppleEPFOpener(urllib.FancyURLopener):
    def prompt_user_passwd(self, host, realm):
        return (APPLE_EPF_USER, APPLE_EPF_PSWD)

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
        
        utils.shell("mkdir -p %s" % APPLE_DATA_DIR)
        
        for link in links:
            suffix = link.get("href")
            #self._init_feed('%s/%s' % (baseurl, suffix), suffix)
            self._pool.spawn(self._init_feed, '%s/%s' % (baseurl, suffix), suffix)
        
        self._pool.join()
    
    def _init_feed(self, url, suffix):
        utils.log(url)
        utils.log(suffix)
        output = os.path.join(APPLE_DATA_DIR, suffix)
        
        cmd = "curl --user %s:%s %s -o %s" % (APPLE_EPF_USER, APPLE_EPF_PSWD, url, output)
        utils.log(cmd)
        utils.shell(cmd)
        
        cmd = "cd %s && tar -xvf %s" % (APPLE_DATA_DIR, suffix)
        utils.log(cmd)
        utils.shell(cmd)
        
        unpacked = suffix[:-4]
        cmd = "cd %s && mkdir -p archive && mv %s archive && mv -f %s/* ./" % (APPLE_DATA_DIR, suffix, unpacked)
        utils.log(cmd)
        utils.shell(cmd)
    
    def getMaxNumEntities(self):
        raise NotImplementedError
    
    def _run(self):
        pass

class AAppleEPFDump(AExternalDumpEntitySource):
    
    def __init__(self, name, entityMap, types, filename):
        AExternalDumpEntitySource.__init__(self, name, types, 512)
        self._filename = filename
        self._columnMap = entityMap
    
    def _open_file(self):
        filename = os.path.join(APPLE_DATA_DIR, self._filename)
        f = open(filename, 'r+b')
        numLines = max(0, CSVUtils.getNumLines(f) - 8)
        
        return f, numLines, filename
    
    def getMaxNumEntities(self):
        f, numLines, filename = self._open_file()
        f.close()
        
        return numLines
    
    def _run(self):
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
        'artist_type_id'    : 'artist_type_id', 
    }
    
    def __init__(self):
        AAppleEPFDump.__init__(self, "Apple EPF Artists", self._map, [ "artist" ], "artist")

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

class AppleEPFCollectionType(AAppleEPFDump):
    
    def __init__(self):
        AAppleEPFDump.__init__(self, "Apple EPF Albums", None, [ ], "collection_type")
        self.collection_types = { }
    
    def _parseRow(self, row, table_format):
        name = row[table_format.cols.name.index]
        self.collection_types[name] = row[table_format.cols.collection_type_id.index]

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
        
        g = AppleEPFCollectionType()
        g.start()
        g.join()
        self.album_type_id = g.collection_types['Album']
    
    def _filter(self, row, table_format):
        # TODO: figure out why some albums are malformed
        try:
            collection_type_id = row[table_format.cols.collection_type_id.index]
            
            # only retain album collections
            return collection_type_id == self.album_type_id
        except IndexError:
            return False

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
    }
    
    def __init__(self):
        AAppleEPFDump.__init__(self, "Apple EPF Videos", self._map, [ "video" ], "video")

import EntitySources
#EntitySources.registerSource('apple', AppleEPFDumps)
EntitySources.registerSource('apple_artists', AppleEPFArtistDump)
EntitySources.registerSource('apple_songs', AppleEPFSongDump)
EntitySources.registerSource('apple_albums', AppleEPFAlbumDump)
EntitySources.registerSource('apple_videos', AppleEPFVideoDump)

