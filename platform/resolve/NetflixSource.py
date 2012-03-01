#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'NetflixSource', 'NetflixMovie' ]

import Globals
from logs import report

try:
    from libs.Netflix               import globalNetflix
    from GenericSource              import GenericSource
    from utils                      import lazyProperty
    from gevent.pool                import Pool
    import logs
    from Resolver                   import *
except:
    report()
    raise


class _NetflixObject(object):
    """
    Abstract superclass (mixin) for Spotify objects.

    _SpotifyObjects must be instantiated with their valid spotify_id.

    Attributes:

    spotify - an instance of Spotify (API wrapper)
    """

    def __init__(self, netflix_id):
        self.__nef

    @lazyProperty
    def netflix(self):
        return globalNetflix()

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
        pool = Pool(min(len(self.albums),20))
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


class SpotifySource(GenericSource):
    """
    """
    def __init__(self):
        GenericSource.__init__(self, 'spotify')

    @lazyProperty
    def __spotify(self):
        return globalSpotify()

    def matchSource(self, query):
        if query.type == 'artist':
            return self.artistSource(query)
        elif query.type == 'album':
            return self.albumSource(query)
        elif query.type == 'track':
            return self.trackSource(query)
        else:
            return self.emptySource

    def trackSource(self, query):
        tracks = self.__spotify.search('track',q=query.name)['tracks']
        def source(start, count):
            if start + count <= len(tracks):
                result = tracks[start:start+count]
            elif start < len(tracks):
                result = tracks[start:]
            else:
                result = []
            return [ SpotifyTrack( entry['href'] ) for entry in result ]
        return source

    
    def albumSource(self, query):
        albums = self.__spotify.search('album',q=query.name)['albums']
        def source(start, count):
            if start + count <= len(albums):
                result = albums[start:start+count]
            elif start < len(albums):
                result = albums[start:]
            else:
                result = []
            return [ SpotifyAlbum( entry['href'] ) for entry in result if entry['availability']['territories'].find('US') != -1 ]
        return source


    def artistSource(self, query):
        artists = self.__spotify.search('artist',q=query.name)['artists']
        def source(start, count):
            if start + count <= len(artists):
                result = artists[start:start+count]
            elif start < len(artists):
                result = artists[start:]
            else:
                result = []
            return [ SpotifyArtist( entry['href'] ) for entry in result ]
        return source

if __name__ == '__main__':
    demo(SpotifySource(), 'Katy Perry')
