#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'SpotifySource', 'SpotifyArtist', 'SpotifyAlbum', 'SpotifyTrack' ]

import Globals, utils
from logs import report

try:
    import logs
    from libs.Spotify               import globalSpotify
    from copy                       import copy
    from GenericSource              import GenericSource, multipleSource, listSource
    from utils                      import lazyProperty
    from gevent.pool                import Pool
    from Resolver                   import *
    from ResolverObject             import *
    from pprint                     import pformat
except:
    report()
    raise


class _SpotifyObject(object):
    """
    Abstract superclass (mixin) for Spotify objects.

    _SpotifyObjects must be instantiated with their valid spotify_id.

    Attributes:

    spotify - an instance of Spotify (API proxy)
    """

    def __init__(self, spotify_id, spotify=None):
        if spotify is None:
            spotify = globalSpotify()
        
        self.__spotify    = spotify
        self.__spotify_id = spotify_id

    @property
    def spotify(self):
        return self.__spotify

    @lazyProperty
    def key(self):
        return self.__spotify_id

    @property 
    def source(self):
        return "spotify"

    def __repr__(self):
        # NOTE: availability generally includes *many* ISO country codes which 
        # make sifting through debug printouts painful, so disable them here.
        data = copy(self.data)
        data.pop('availability', None)
        return "<%s %s %s> %s" % (self.source, self.types, self.name, pformat(data))


class SpotifyArtist(_SpotifyObject, ResolverPerson):
    """
    Spotify artist proxy
    """
    def __init__(self, spotify_id):
        _SpotifyObject.__init__(self, spotify_id)  
        ResolverPerson.__init__(self, types=['artist'])

    @lazyProperty
    def data(self):
        result = self.spotify.lookup(self.key, "albumdetail")
        return result['artist']

    @lazyProperty
    def name(self):
        return self.data['name']

    @lazyProperty
    def albums(self):
        album_list = self.data['albums']
        return [
            {
                'name'  : entry['album']['name'],
                'key'   : entry['album']['href'],
            }
                for entry in album_list
                    if entry['album']['artist'] == self.name and entry['album']['availability']['territories'].find('US') != -1
        ]

    @lazyProperty
    def tracks(self):
        tracks = {}
        
        def lookupTrack(key):
            result = self.spotify.lookup(key, 'trackdetail')
            track_list = result['album']['tracks']
            
            for track in track_list:
                track_key = track['href']
                
                if track_key not in tracks:
                    data = {
                        'key': track_key,
                        'name': track['name'],
                    }
                    
                    try:
                        # (travis): as of 4/3/12, track length is only sometimes returned by spotify
                        data['length'] = int(track['length']),
                    except KeyError:
                        pass
                    
                    tracks[track_key] = data
        
        size = min(1 + len(self.albums), 20)
        pool = Pool(size)
        
        for album in self.albums:
            key = album['key']
            pool.spawn(lookupTrack, key)
        
        pool.join()
        return list(tracks.values())


class SpotifyAlbum(_SpotifyObject, ResolverMediaCollection):
    """
    Spotify album proxy
    """
    def __init__(self, spotify_id):
        _SpotifyObject.__init__(self, spotify_id)  
        ResolverMediaCollection.__init__(self, types=['album'])

    @lazyProperty
    def data(self):
        return self.spotify.lookup(self.key, 'trackdetail')['album']

    @lazyProperty
    def name(self):
        return self.data['name']

    @lazyProperty
    def artists(self):
        try:
            return [ { 
                'name'  : self.data['artist'],
                'key'   : self.data['artist-id'],
            } ]
        except Exception:
            return []

    @lazyProperty
    def tracks(self):
        track_list = self.data['tracks']
        return [ 
            { 
                'name'  : track['name'], 
                'key'   : track['href'],
            } 
                for track in track_list 
        ]


class SpotifyTrack(_SpotifyObject, ResolverMediaItem):
    """
    Spotify track proxy
    """
    def __init__(self, spotify_id):
        _SpotifyObject.__init__(self, spotify_id)  
        ResolverMediaItem.__init__(self, types=['track'])

    @lazyProperty
    def data(self):
        return self.spotify.lookup(self.key)['track']

    @lazyProperty
    def name(self):
        return self.data['name']

    @lazyProperty
    def artists(self):
        try:
            return [ { 
                'name'  : self.data['artists'][0]['name'],
                'key'   : self.data['artists'][0]['href'],
            } ]
        except Exception:
            return []

    @lazyProperty
    def albums(self):
        try:
            return [ { 
                'name'  : self.data['album']['name'],
                'key'   : self.data['album']['href'],
            } ]
        except Exception:
            return []

    @lazyProperty
    def length(self):
        try:
            return float(self.data['length'])
        except Exception:
            return -1


class SpotifySearchAll(ResolverProxy, ResolverSearchAll):

    def __init__(self, target):
        ResolverProxy.__init__(self, target)
        ResolverSearchAll.__init__(self)

class SpotifySource(GenericSource):
    """
    """
    def __init__(self):
        GenericSource.__init__(self, 'spotify',
            groups=[
                'albums',
                'tracks',
            ],
            kinds=[
                'person',
                'media_collection',
                'media_item',
            ],
            types=[
                'artist',
                'album',
                'track',
            ]
        )

    @lazyProperty
    def __spotify(self):
        return globalSpotify()

    @property
    def urlField(self):
        return None

    def entityProxyFromKey(self, key, **kwargs):
        try:
            item = self.__spotify.lookup(key)
            
            if item['info']['type'] == 'artist':
                return SpotifyArtist(key)
            if item['info']['type'] == 'album':
                return SpotifyAlbum(key)
            if item['info']['type'] == 'track':
                return SpotifyTrack(key)
            
            raise KeyError
        except KeyError:
            logs.warning('Unable to find Spotify item for key: %s' % key)
            raise
        
        return None

    def enrichEntityWithEntityProxy(self, proxy, entity, controller=None, decorations=None, timestamps=None):
        GenericSource.enrichEntityWithEntityProxy(self, proxy, entity, controller, decorations, timestamps)
        entity.sources.spotify_id = proxy.key
        
        return True

    def matchSource(self, query):
        if query.kind == 'person' and query.isType('artist'):
            return self.artistSource(query)
        if query.kind == 'media_collection' and query.isType('album'):
            return self.albumSource(query)
        if query.kind == 'media_item' and query.isType('track'):
            return self.trackSource(query)
        if query.kind == 'search':
            return self.searchAllSource(query)
        
        return self.emptySource

    def trackSource(self, query=None, query_string=None):
        if query is not None:
            q = query.name
        elif query_string is not None:
            q = query_string
        else:
            raise ValueError("query and query_string cannot both be None")
        
        tracks = self.__spotify.search('track',q=q)['tracks']
        return listSource(tracks, constructor=lambda x: SpotifyTrack( x['href'] ))
    
    def albumSource(self, query=None, query_string=None):
        if query is not None:
            q = query.name
        elif query_string is not None:
            q = query_string
        else:
            raise ValueError("query and query_string cannot both be None")
        
        albums = self.__spotify.search('album',q=q)['albums']
        albums = [ entry for entry in albums if entry['availability']['territories'].find('US') != -1 ]
        return listSource(albums, constructor=lambda x: SpotifyAlbum( x['href'] ))


    def artistSource(self, query=None, query_string=None):
        if query is not None:
            q = query.name
        elif query_string is not None:
            q = query_string
        else:
            raise ValueError("query and query_string cannot both be None")
        
        artists = self.__spotify.search('artist',q=q)['artists']
        return listSource(artists, constructor=lambda x: SpotifyArtist( x['href'] ))

    def searchAllSource(self, query, timeout=None):
        if query.kinds is not None and len(query.kinds) > 0 and len(self.kinds.intersection(query.kinds)) == 0:
            logs.debug('Skipping %s (kinds: %s)' % (self.sourceName, query.kinds))
            return self.emptySource

        if query.types is not None and len(query.types) > 0 and len(self.types.intersection(query.types)) == 0:
            logs.debug('Skipping %s (types: %s)' % (self.sourceName, query.types))
            return self.emptySource

        logs.debug('Searching %s...' % self.sourceName)
            
        q = query.query_string
        return multipleSource(
            [
                lambda : self.artistSource(query_string=q),
                lambda : self.albumSource(query_string=q),
                lambda : self.trackSource(query_string=q),
            ],
            constructor=SpotifySearchAll
        )

if __name__ == '__main__':
    demo(SpotifySource(), 'Katy Perry')

