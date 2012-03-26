#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'SpotifySource', 'SpotifyArtist', 'SpotifyAlbum', 'SpotifyTrack' ]

import Globals
from logs import report

try:
    from libs.Spotify               import globalSpotify
    from GenericSource              import GenericSource, multipleSource, listSource
    from utils                      import lazyProperty
    from gevent.pool                import Pool
    import logs
    from Resolver                   import *
    from pprint                     import pformat
except:
    report()
    raise


class _SpotifyObject(object):
    """
    Abstract superclass (mixin) for Spotify objects.

    _SpotifyObjects must be instantiated with their valid spotify_id.

    Attributes:

    spotify - an instance of Spotify (API wrapper)
    """

    def __init__(self, spotify_id, spotify=None):
        if spotify is None:
            spotify = globalSpotify()
        self.__spotify = spotify
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
        return "<%s %s %s>" % (self.source, self.type, self.name)


class SpotifyArtist(_SpotifyObject, ResolverArtist):
    """
    Spotify artist wrapper
    """
    def __init__(self, spotify_id):
        _SpotifyObject.__init__(self, spotify_id)  
        ResolverArtist.__init__(self)

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
                'name':entry['album']['name'],
                'key':entry['album']['href'],
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
                    tracks[track_key] = {
                        'name': track['name'],
                    }
        pool = Pool(min(1+len(self.albums),20))
        for album in self.albums:
            key = album['key']
            pool.spawn(lookupTrack, key)
        pool.join()
        return list(tracks.values())


class SpotifyAlbum(_SpotifyObject, ResolverAlbum):
    """
    Spotify album wrapper
    """
    def __init__(self, spotify_id):
        _SpotifyObject.__init__(self, spotify_id)  
        ResolverAlbum.__init__(self)

    @lazyProperty
    def data(self):
        return self.spotify.lookup(self.key, 'trackdetail')['album']

    @lazyProperty
    def name(self):
        return self.data['name']

    @lazyProperty
    def artist(self):
        return { 'name': self.data['artist'] }

    @lazyProperty
    def tracks(self):
        track_list = self.data['tracks']
        return [
            {
                'name':track['name'],
            }
                for track in track_list
        ]


class SpotifyTrack(_SpotifyObject, ResolverTrack):
    """
    Spotify track wrapper
    """
    def __init__(self, spotify_id):
        _SpotifyObject.__init__(self, spotify_id)  
        ResolverTrack.__init__(self)

    @lazyProperty
    def data(self):
        return self.spotify.lookup(self.key)['track']

    @lazyProperty
    def name(self):
        return self.data['name']

    @lazyProperty
    def artist(self):
        try:
            return {'name': self.data['artists'][0]['name'] }
        except Exception:
            return {'name':''}

    @lazyProperty
    def album(self):
        return {'name':self.data['album']['name']}

    @lazyProperty
    def length(self):
        return float(self.data['length'])


class SpotifySearchAll(ResolverProxy, ResolverSearchAll):

    def __init__(self, target):
        ResolverProxy.__init__(self, target)
        ResolverSearchAll.__init__(self)

    @property
    def subtype(self):
        return self.target.type

class SpotifySource(GenericSource):
    """
    """
    def __init__(self):
        GenericSource.__init__(self, 'spotify')

    @lazyProperty
    def __spotify(self):
        return globalSpotify()

    @property
    def urlField(self):
        return None

    def wrapperFromKey(self, key, type=None):
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
            logs.warning('UNABLE TO FIND SPOTIFY ITEM FOR ID: %s' % key)
            raise
        return None

    def enrichEntityWithWrapper(self, wrapper, entity, controller=None, decorations=None, timestamps=None):
        GenericSource.enrichEntityWithWrapper(self, wrapper, entity, controller, decorations, timestamps)
        entity.spotify_id = wrapper.key
        return True

    def matchSource(self, query):
        if query.type == 'artist':
            return self.artistSource(query)
        elif query.type == 'album':
            return self.albumSource(query)
        elif query.type == 'track':
            return self.trackSource(query)
        elif query.type == 'search_all':
            return self.searchAllSource(query)
        else:
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

    def searchAllSource(self, query, timeout=None, types=None):
        validTypes = set(['track', 'album', 'artist'])
        if types is not None and len(validTypes.intersection(types)) == 0:
            return self.emptySource
            
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

