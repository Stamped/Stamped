#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'RdioSource', 'RdioArtist', 'RdioAlbum', 'RdioTrack' ]

import Globals
from logs import report

try:
    from libs.Rdio                  import Rdio, globalRdio
    from GenericSource              import GenericSource
    from utils                      import lazyProperty
    import logs
    from Resolver                   import *
    from pprint                     import pformat
except:
    report()
    raise


class _RdioObject(object):
    """
    Abstract superclass (mixin) for Rdio objects.

    _RdioObjects can be instatiated with either the rdio_id or the rdio data for an entity.
    If both are provided, they must match. extras may be used to retrieve additional data
    when instantiating an object using only its id.

    Attributes:

    data - the type-specific rdio data for the entity
    rdio - an instance of Rdio (API wrapper)
    """

    def __init__(self, data=None, rdio_id=None, rdio=None, extras=''):
        if rdio is None:
            rdio = globalRdio()
        if data == None:
            if rdio_id is None:
                raise ValueError('data or rdio_id must not be None')
            try:
                data = rdio.method('get',keys=rdio_id,extras=extras)['result'][rdio_id]
            except KeyError:
                raise ValueError('bad rdio_id')
        elif rdio_id is not None:
            if rdio_id != data['key']:
                raise ValueError('rdio_id does not match data["key"]')
        self.__rdio = rdio
        self.__data = data

    @property
    def rdio(self):
        return self.__rdio

    @property
    def data(self):
        return self.__data

    @lazyProperty
    def name(self):
        return self.data['name']

    @lazyProperty
    def key(self):
        return self.data['key']

    @lazyProperty
    def url(self):
        return self.data['url']

    @property 
    def source(self):
        return "rdio"

    def __repr__(self):
        return pformat( self.data )


class RdioArtist(_RdioObject, ResolverArtist):
    """
    Rdio artist wrapper
    """
    def __init__(self, data=None, rdio_id=None, rdio=None):
        _RdioObject.__init__(self, data=data, rdio_id=rdio_id, rdio=rdio, extras='albumCount')  
        ResolverArtist.__init__(self)

    @lazyProperty
    def albums(self):
        album_list = self.rdio.method('getAlbumsForArtist',artist=self.key,count=100)['result']
        return [ {'name':entry['name']} for entry in album_list ]

    @lazyProperty
    def tracks(self):
        track_list = self.rdio.method('getTracksForArtist',artist=self.key,count=100)['result']
        return [ {'name':entry['name']} for entry in track_list ]

class RdioAlbum(_RdioObject, ResolverAlbum):
    """
    Rdio album wrapper
    """
    def __init__(self, data=None, rdio_id=None, rdio=None):
        _RdioObject.__init__(self, data=data, rdio_id=rdio_id, rdio=rdio, extras='label, isCompilation')
        ResolverAlbum.__init__(self)

    @lazyProperty
    def artist(self):
        return { 'name' : self.data['artist'] }

    @lazyProperty
    def tracks(self):
        keys = ','.join(self.data['trackKeys'])
        track_dict = self.rdio.method('get',keys=keys)['result']
        return [ {'name':entry['name']} for k, entry in track_dict.items() ]


class RdioTrack(_RdioObject, ResolverTrack):
    """
    Rdio track wrapper
    """
    def __init__(self, data=None, rdio_id=None, rdio=None):
        _RdioObject.__init__(self, data=data, rdio_id=rdio_id, rdio=rdio, extras='label, isCompilation')
        ResolverTrack.__init__(self)

    @lazyProperty
    def artist(self):
        return {'name':self.data['artist']}

    @lazyProperty
    def album(self):
        return {'name':self.data['album']}

    @lazyProperty
    def length(self):
        return float(self.data['duration'])


class RdioSource(GenericSource):
    """
    """
    def __init__(self):
        GenericSource.__init__(self, 'rdio')

    @lazyProperty
    def __rdio(self):
        return globalRdio()

    def wrapperFromData(self, data):
        if data['type'] == 'r':
            return RdioArtist(data=data)
        elif data['type'] == 'a':
            return RdioAlbum(data=data)
        elif data['type'] == 't':
            return RdioTrack(data=data)
        else:
            return None
    
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
