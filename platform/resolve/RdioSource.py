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
    from MusicSource                import MusicSource
    from utils                      import lazyProperty
    import logs
    from pprint                     import pprint, pformat
    import sys
    from Resolver                   import Resolver, RdioArtist, RdioAlbum, RdioTrack
except:
    report()
    raise

_verbose = False
_very_verbose = False

class RdioSource(MusicSource):
    """
    """
    def __init__(self):
        MusicSource.__init__(self, 'rdio')

    @lazyProperty
    def __rdio(self):
        return globalRdio()
    
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
                if _verbose:
                    pprint(entries)
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
                if _verbose:
                    pprint(entries)
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
                if _verbose:
                    pprint(entries)
                return [ RdioArtist( data=entry, rdio=self.__rdio ) for entry in entries ]
            else:
                return []
        return source

if __name__ == '__main__':
    RdioSource().demo()
