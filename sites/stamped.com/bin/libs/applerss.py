#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals
import copy, json, re, urllib, utils

from Schemas    import *
from pprint     import pprint
from libs.apple import AppleAPI

__all__ = [ "AppleRSS", "AppleRSSError" ]

class AppleRSSError(Exception):
    pass

class AppleRSS(object):
    
    DEFAULT_FORMAT = 'json'
    
    _subcategory_map = {
        'artist'        : 'artist', 
        'track'         : 'song', 
        'album'         : 'album', 
        'application'   : 'app', 
    }
    
    _webobject_feeds = set([
        'newreleases', 
        'justadded', 
    ])
    
    def __init__(self):
        self._id_re = re.compile('.*\/id([0-9]+).*')
        self._apple = AppleAPI(country='us')
    
    def get_top_albums(self, **kwargs):
        return self._parse_feed('topalbums', **kwargs)
    
    def get_top_songs(self, **kwargs):
        return self._parse_feed('topsongs', **kwargs)
    
    def get_top_free_apps(self, **kwargs):
        return self._parse_feed('topfreeapplications', **kwargs)
    
    def get_top_paid_apps(self, **kwargs):
        return self._parse_feed('toppaidapplications', **kwargs)
    
    def get_top_grossing_apps(self, **kwargs):
        return self._parse_feed('topgrossingapplications', **kwargs)
    
    def get_new_releases(self, **kwargs):
        return self._parse_feed('newreleases', **kwargs)
    
    def get_just_added(self, **kwargs):
        return self._parse_feed('justadded', **kwargs)
    
    def _parse_feed(self, feedname, **kwargs):
        webobject = (feedname in self._webobject_feeds)
        
        # extract keyword arguments and defaults
        region      = kwargs.pop('region', 'us')
        limit       = kwargs.pop('limit', 10)
        genre       = kwargs.pop('genre', None)
        explicit    = kwargs.pop('explicit', True)
        transform   = kwargs.pop('transform', 1)
        format      = kwargs.pop('format', 'xml' if webobject else self.DEFAULT_FORMAT)
        
        if format not in [ 'xml', 'json' ]:
            raise AppleRSSError("invalid request format")
        
        if webobject:
            url = 'http://itunes.apple.com/WebObjects/MZStore.woa/wpa/MRSS/%s/sf=143441/' % (feedname, )
        else:
            url = 'http://itunes.apple.com/%s/rss/%s/' % (region, feedname)
        
        if limit is not None:
            url = '%slimit=%d/' % (url, limit)
        
        if genre is not None:
            url = '%sgenre=%s/' % (url, genre)
        
        if explicit is not None:
            url = '%sexplicit=%s/' % (url, str(explicit).lower())
        
        if webobject:
            url += 'rss.%s' % format
        else:
            url += format
        
        # attempt to download feed
        utils.log(url)
        data = utils.getFile(url)
        
        """
        f=open('out.xml', 'w')
        f.write(data)
        f.close()
        """
        
        if 0 == transform:
            return data
        
        try:
            data = json.loads(data)
        except ValueError:
            utils.log(data)
            return []
        
        entries  = data['feed']['entry']
        entities = []
        full     = (2 == transform)
        #print json.dumps(entries, indent=2)
        
        if isinstance(entries, dict):
            entries = [ entries ]
        
        for entry in entries:
            try:
                entity = self._parse_entity(entry, full=full)
                if entity is not None:
                    entities.append(entity)
            except:
                pass
        
        return entities
    
    def _parse_entity(self, entry, full=False):
        entity = Entity()
        entity.title = entry['im:name']['label']
        
        details_map = {
            'artist_display_name'   : [ 'im:artist', 'label' ], 
            'artist_id'             : [ 'im:artist', 'attributes', 'href' ], 
            'genre'                 : [ 'category', 'attributes', 'term' ], 
            'original_release_date' : [ 'im:releaseDate', 'attributes', 'label' ], 
            'label_studio'          : [ 'rights', 'label' ], 
            'subcategory'           : ([ 'im:contentType', 'im:contentType', 'attributes', 'term' ], 
                                       [ 'im:contentType', 'attributes', 'term' ], ), 
            'album_name'            : [ 'im:collection', 'im:name', 'label' ], 
            'desc'                  : [ 'summary', 'label' ], 
        }
        
        # parse entity details
        for k, v in details_map.iteritems():
            
            v3 = v
            if not isinstance(v, tuple):
                v3 = [ v ]
            
            for v in v3:
                e = entry
                
                try:
                    for v2 in v:
                        e = e[v2]
                    
                    if e is not None:
                        entity[k] = e
                        break
                except:
                    pass
        
        try:
            entity.subcategory = self._subcategory_map[entity.subcategory.lower()]
        except:
            return None
        
        if entity.artist_id is not None:
            entity.artist_id = self._get_id(entity.artist_id)
        
        # parse largest image available for this entity
        try:
            height = -1
            
            for image in entry['im:image']:
                cur_height = int(image['attributes']['height'])
                
                if cur_height > height:
                    height = cur_height
                    entity.image = image['label']
            
            if entity.image is not None and entity.subcategory != 'app':
                entity.image = entity.image.replace('100x100', '200x200').replace('170x170', '200x200')
        except:
            utils.printException()
            pass
        
        entity.aid = self._get_id(entry['id']['label'])
        
        # parse links (view_url, preview_url)
        links = entry['link']
        if not isinstance(links, list):
            links = [ links ]
        
        for link in links:
            try:
                href = link['attributes']['href']
                
                if 'im:duration' in link:
                    if link['attributes']['im:assetType'].lower() == 'preview':
                        if entity.subcategory == 'app':
                            entity.screenshots = [ href ]
                        else:
                            entity.preview_url = href
                            entity.preview_length = link['im:duration']['label']
                else:
                    entity.view_url = href
            except:
                utils.printException()
                utils.log(json.dumps(entry['link'], indent=2))
                pass
        
        # parse song-specific fields
        if entity.subcategory == 'song':
            album_url = entry['im:collection']['link']['attributes']['href']
            entity.song_album_id = self._get_id(album_url)
        
        # optionally parse extra entity data via apple API
        if full and entity.aid is not None:
            if entity.subcategory == 'album':
                self.parse_album(entity)
            elif entity.subcategory == 'artist':
                self.parse_artist(entity)
            elif entity.subcategory == 'song':
                self.parse_song(entity)
        
        return entity
    
    def _get_id(self, s):
        match = self._id_re.match(s)
        if match is not None:
            return match.groups()[0]
        
        return None
    
    def parse_album(self, entity):
        assert entity.subcategory == 'album'
        
        results = self._apple.lookup(id=entity.aid, media='music', entity='song', transform=True)
        results = filter(lambda r: r.entity.subcategory == 'song', results)
        
        entity.tracks = list(result.entity.title for result in results)
    
    def parse_song(self, entity):
        assert entity.subcategory == 'song'
        pass
    
    def parse_artist(self, entity):
        assert entity.subcategory == 'artist'
        
        results = self._apple.lookup(id=entity.aid, media='music', entity='album', limit=200, transform=True)
        results = filter(lambda r: r.entity.subcategory == 'album', results)
        
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
        
        results = self._apple.lookup(id=entity.aid, media='music', entity='song', limit=200, transform=True)
        results = filter(lambda r: r.entity.subcategory == 'song', results)
        
        songs = []
        for result in results:
            schema = ArtistSongsSchema()
            schema.song_id   = result.entity.aid
            schema.song_name = result.entity.title
            songs.append(schema)
        
        entity.songs = songs

def main():
    rss = AppleRSS()
    #ret = rss.get_top_albums(limit=10, transform=2)
    ret = rss.get_top_songs(limit=10, transform=2)
    
    for entity in ret:
        pprint(entity.value)

if __name__ == '__main__':
    main()

