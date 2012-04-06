#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'RdioSource', 'RdioArtist', 'RdioAlbum', 'RdioTrack', 'RdioSearchAll' ]

import Globals
from logs import report

try:
    import logs
    from Resolver                   import *
    from ResolverObject             import *
    from libs.Rdio                  import Rdio, globalRdio
    from GenericSource              import GenericSource
    from utils                      import lazyProperty
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
    rdio - an instance of Rdio (API proxy)
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


class RdioArtist(_RdioObject, ResolverPerson):
    """
    Rdio artist proxy
    """
    def __init__(self, data=None, rdio_id=None, rdio=None):
        _RdioObject.__init__(self, data=data, rdio_id=rdio_id, rdio=rdio, extras='albumCount')  
        ResolverPerson.__init__(self, types=['artist'])

    @lazyProperty
    def albums(self):
        album_list = self.rdio.method('getAlbumsForArtist',artist=self.key,count=100)['result']
        return [ {'name':entry['name']} for entry in album_list ]

    @lazyProperty
    def tracks(self):
        track_list = self.rdio.method('getTracksForArtist',artist=self.key,count=100)['result']
        return [ {'name':entry['name']} for entry in track_list ]

class RdioAlbum(_RdioObject, ResolverMediaCollection):
    """
    Rdio album proxy
    """
    def __init__(self, data=None, rdio_id=None, rdio=None):
        _RdioObject.__init__(self, data=data, rdio_id=rdio_id, rdio=rdio, extras='label, isCompilation')
        ResolverMediaCollection.__init__(self, types=['album'])

    @lazyProperty
    def artists(self):
        try:
            return [ { 'name' : self.data['artist'] } ]
        except Exception:
            return []

    @lazyProperty
    def tracks(self):
        keys = ','.join(self.data['trackKeys'])
        track_dict = self.rdio.method('get',keys=keys)['result']
        return [ {'name':entry['name']} for k, entry in track_dict.items() ]


class RdioTrack(_RdioObject, ResolverMediaItem):
    """
    Rdio track proxy
    """
    def __init__(self, data=None, rdio_id=None, rdio=None):
        _RdioObject.__init__(self, data=data, rdio_id=rdio_id, rdio=rdio, extras='label, isCompilation')
        ResolverMediaItem.__init__(self, types=['track'])

    @lazyProperty
    def artists(self):
        return [ { 'name':self.data['artist'] } ]

    @lazyProperty
    def albums(self):
        return [ { 'name':self.data['album'] } ]

    @lazyProperty
    def length(self):
        return float(self.data['duration'])


class RdioSearchAll(ResolverProxy, ResolverSearchAll):

    def __init__(self, data):
        target = None
        t = data['type']
        if t == 't':
            target = RdioTrack(data=data)
        elif t == 'a':
            target = RdioAlbum(data=data)
        elif t == 'r':
            target = RdioArtist(data=data)
        else:
            raise ValueError("bad type for Rdio data: %s" % data)
        ResolverProxy.__init__(self, target)
        ResolverSearchAll.__init__(self)

class RdioSource(GenericSource):
    """
    """
    def __init__(self):
        GenericSource.__init__(self, 'rdio', 
            groups=[
                'album_list',
                'track_list',
            ],
            types=[
                'artist',
                'album',
                'track',
            ]
        )

    @lazyProperty
    def __rdio(self):
        return globalRdio()

    def entityProxyFromKey(self, key):
        try:
            if key.startswith('t'):
                return RdioTrack(rdio_id=key)
            if key.startswith('a'):
                return RdioAlbum(rdio_id=key)
            if key.startswith('r'):
                return RdioArtist(rdio_id=key)
            raise KeyError
        except KeyError:
            logs.warning('Unable to find rdio item for key: %s' % key)
            raise
        return None

    def entityProxyFromData(self, data):
        if data['type'] == 'r':
            return RdioArtist(data=data)
        elif data['type'] == 'a':
            return RdioAlbum(data=data)
        elif data['type'] == 't':
            return RdioTrack(data=data)
        else:
            return None

    def enrichEntityWithEntityProxy(self, proxy, entity, controller=None, decorations=None, timestamps=None):
        GenericSource.enrichEntityWithEntityProxy(self, proxy, entity, controller, decorations, timestamps)
        entity.rdio_id = proxy.key
        return True
    
    def matchSource(self, query):
        if query.isType('artist'):
            return self.artistSource(query)
        if query.isType('album'):
            return self.albumSource(query)
        if query.isType('track'):
            return self.trackSource(query)
        if query.kind == 'search':
            return self.searchAllSource(query)
        
        return self.emptySource

    def trackSource(self, query):
        return self.generatorSource(self.__queryGen(
                query=query.name,
                types='Track',
                extras='',
            ),
            constructor=RdioTrack)
    
    def albumSource(self, query):
        return self.generatorSource(self.__queryGen(
                query=query.name,
                types='Album',
                extras='label,isCompilation',
            ),
            constructor=RdioAlbum)

    def artistSource(self, query):
        return self.generatorSource(self.__queryGen(
                query=query.name,
                types='Artist',
                extras='albumCount',
            ),
            constructor=RdioArtist)

    def searchAllSource(self, query, timeout=None):
        if query.types is not None and len(self.types.intersection(query.types)) == 0:
            return self.emptySource
        
        return self.generatorSource(self.__queryGen(
                query=query.query_string,
                types='Artist,Album,Track',
                extras='albumCount,label,isCompilation',
            ),
            constructor=RdioSearchAll)
    
    def __queryGen(self, batches=(100,), **params):
        def gen():
            try:
                batches = [100]
                offset  = 0
                
                for batch in batches:
                    response = self.__rdio.method('search',
                        start=offset,
                        count=batch,
                        **params
                    )
                    if response['status'] == 'ok':
                        entries = response['result']['results']
                        for entry in entries:
                            yield entry
                    else:
                        break
                    offset += batch
            except GeneratorExit:
                pass
        return gen()

if __name__ == '__main__':
    demo(RdioSource(), 'Katy Perry')

