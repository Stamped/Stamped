#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'RdioSource' ]

import Globals
from logs import report

try:
    from libs.Rdio                  import Rdio, globalRdio
    from GenericSource              import GenericSource
    from utils                      import lazyProperty
    import logs
    from Resolver                   import Resolver, RdioArtist, RdioAlbum, RdioTrack, demo
except:
    report()
    raise

class RdioSource(GenericSource):
    """
    """
    def __init__(self):
        GenericSource.__init__(self, 'rdio')

    @lazyProperty
    def __rdio(self):
        return globalRdio()
    
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
        name = query.name
        def source(start, count):
            response = self.__rdio.method('search',
                query=name,
                types='Track',
                extras='',
                start=start,
                count=count,
            )
            if response['status'] == 'ok':
                entries = response['result']['results']
                return [ RdioTrack( data=entry, rdio=self.__rdio ) for entry in entries ]
            else:
                return []
        return source
    
    def albumSource(self, query):
        name = query.name
        def source(start, count):
            response = self.__rdio.method('search',
                query=name,
                types='Album',
                extras='label, isCompilation',
                start=start,
                count=count,
            )
            if response['status'] == 'ok':
                entries = response['result']['results']
                return [ RdioAlbum( data=entry, rdio=self.__rdio ) for entry in entries ]
            else:
                return []
        return source

    def artistSource(self, query):
        name = query.name
        def source(start, count):
            response = self.__rdio.method('search',
                query=name,
                types='Artist',
                extras='albumCount',
                start=start,
                count=count,
            )
            if response['status'] == 'ok':
                entries = response['result']['results']
                return [ RdioArtist( data=entry, rdio=self.__rdio ) for entry in entries ]
            else:
                return []
        return source

if __name__ == '__main__':
    demo(RdioSource(), 'Katy Perry')
