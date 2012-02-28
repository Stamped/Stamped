#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'iTunesSource' ]

import Globals
from logs import report

try:
    from libs.iTunes                import globaliTunes
    from GenericSource                import GenericSource
    from utils                      import lazyProperty
    import logs
    from pprint                     import pprint, pformat
    import sys
    from Resolver                   import Resolver, iTunesArtist, iTunesAlbum, iTunesTrack, demo
except:
    report()
    raise

class iTunesSource(GenericSource):
    """
    """
    def __init__(self):
        GenericSource.__init__(self, 'itunes')

    @lazyProperty
    def __itunes(self):
        return globaliTunes()

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
        tracks = self.__itunes.method('search',term=query.name, entity='song', attribute='allTrackTerm', limit=200)['results']
        def source(start, count):
            if start + count <= len(tracks):
                result = tracks[start:start+count]
            elif start < len(tracks):
                result = tracks[start:]
            else:
                result = []
            return [ iTunesTrack( entry['trackId'] ) for entry in result ]
        return source

    
    def albumSource(self, query):
        albums = self.__itunes.method('search',term=query.name, entity='album', attribute='albumTerm', limit=200)['results']
        def source(start, count):
            if start + count <= len(albums):
                result = albums[start:start+count]
            elif start < len(albums):
                result = albums[start:]
            else:
                result = []
            return [ iTunesAlbum( entry['collectionId'] ) for entry in result ]
        return source


    def artistSource(self, query):
        artists = self.__itunes.method('search',term=query.name, entity='allArtist', attribute='allArtistTerm', limit=100)['results']
        def source(start, count):
            if start + count <= len(artists):
                result = artists[start:start+count]
            elif start < len(artists):
                result = artists[start:]
            else:
                result = []
            return [ iTunesArtist( entry['artistId'] ) for entry in result ]
        return source

if __name__ == '__main__':
    demo(iTunesSource(), 'Katy Perry')
