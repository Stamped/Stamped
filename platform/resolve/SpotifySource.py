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
    from MusicSource                import MusicSource
    from utils                      import lazyProperty
    import logs
    from pprint                     import pprint, pformat
    import sys
    from Resolver                   import Resolver, SpotifyArtist, SpotifyAlbum, SpotifyTrack
except:
    report()
    raise

_verbose = False
_very_verbose = False

class SpotifySource(MusicSource):
    """
    """
    def __init__(self):
        MusicSource.__init__(self, 'spotify')

    @lazyProperty
    def __spotify(self):
        return globalSpotify()

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
    SpotifySource().demo()
