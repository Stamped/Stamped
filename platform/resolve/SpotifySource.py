#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'SpotifySource' ]

import Globals
from logs import report

try:
    from libs.Spotify               import globalSpotify
    from GenericSource              import GenericSource
    from utils                      import lazyProperty
    import logs
    from Resolver                   import Resolver, SpotifyArtist, SpotifyAlbum, SpotifyTrack, demo
except:
    report()
    raise

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
            return [ SpotifyAlbum( entry['href'] ) for entry in result ]
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
