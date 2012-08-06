#!/usr/bin/env python
from __future__ import absolute_import

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
    from resolve.Resolver           import *
    from resolve.ResolverObject     import *
    from resolve.TitleUtils         import *
    from libs.Rdio                  import Rdio, globalRdio
    from resolve.GenericSource      import GenericSource, MERGE_TIMEOUT, SEARCH_TIMEOUT
    from utils                      import lazyProperty
    from pprint                     import pformat
    from search.ScoringUtils        import *
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

    def __init__(self, data=None, rdio_id=None, rdio=None, extras='', timeout=None):
        if rdio is None:
            rdio = globalRdio()
        if data == None:
            if rdio_id is None:
                raise ValueError('data or rdio_id must not be None')
            try:
                # NOTE: The fact that I'm (disgracefully) calling a ResolverObject method from within _RdioObject's
                # __init__ means that all subclassers must first init ResolverObject or a subclass before initing
                # _RdioObject.
                self.countLookupCall('main data')
                data = rdio.method('get', keys=rdio_id, extras=extras, timeout=timeout)['result'][rdio_id]
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
    def raw_name(self):
        return self.data['name']

    @lazyProperty
    def key(self):
        return self.data['key']

    @lazyProperty
    def url(self):
        return 'http://www.rdio.com%s' % self.data['url']

    @lazyProperty
    def canStream(self):
        try:
            return self.data['canStream']
        except Exception:
            return False

    @lazyProperty
    def canSample(self):
        try:
            return self.data['canStream']
        except Exception:
            return False

    @property 
    def source(self):
        return "rdio"

    @lazyProperty
    def images(self):
        try:
            image = self.data['icon']
            if 'no-artist-image' in image:
                return []
            return [ image ]
        except Exception:
            return []

    def __repr__(self):
        return pformat( self.data )


class RdioArtist(_RdioObject, ResolverPerson):
    """
    Rdio artist proxy
    """
    def __init__(self, data=None, rdio_id=None, rdio=None, maxLookupCalls=None):
        ResolverPerson.__init__(self, types=['artist'], maxLookupCalls=maxLookupCalls)
        _RdioObject.__init__(self, data=data, rdio_id=rdio_id, rdio=rdio, extras='albumCount')

    def _cleanName(self, rawName):
        return cleanArtistTitle(rawName)

    @lazyProperty
    def albums(self):
        try:
            self.countLookupCall('albums')
            album_list = self.rdio.method('getAlbumsForArtist', artist=self.key, count=100, timeout=MERGE_TIMEOUT)['result']
        except LookupRequiredError:
            return []
        return [ 
            {
                'name'  : entry['name'],
                'key'   : entry['key'],
                'url'   : 'http://rdio.com%s' % entry['url'],
            } 
                for entry in album_list 
        ]

    @lazyProperty
    def tracks(self):
        try:
            self.countLookupCall('tracks')
            track_list = self.rdio.method('getTracksForArtist', artist=self.key, count=100, timeout=MERGE_TIMEOUT)['result']
        except LookupRequiredError:
            return []
        return [ 
            {
                'name'  : entry['name'],
                'key'   : entry['key'],
                'url'   : 'http://rdio.com%s' % entry['url'],
            } 
                for entry in track_list 
        ]

class RdioAlbum(_RdioObject, ResolverMediaCollection):
    """
    Rdio album proxy
    """
    def __init__(self, data=None, rdio_id=None, rdio=None, maxLookupCalls=None):
        ResolverMediaCollection.__init__(self, types=['album'], maxLookupCalls=maxLookupCalls)
        _RdioObject.__init__(self, data=data, rdio_id=rdio_id, rdio=rdio, extras='label, isCompilation')

    def _cleanName(self, rawName):
        return cleanAlbumTitle(rawName)

    @lazyProperty
    def artists(self):
        result = {}
        try:
            result['name']  = self.data['artist']
            result['key']   = self.data['artistKey']
            result['url']   = 'http://rdio.com%s' % self.data['artistUrl']
            return [ result ]
        except Exception:
            return []

    @lazyProperty
    def tracks(self):
        try:
            keys = ','.join(self.data['trackKeys'])
            self.countLookupCall('tracks')
            track_dict = self.rdio.method('get', keys=keys, timeout=MERGE_TIMEOUT)['result']
        except LookupRequiredError:
            return []
        return [ 
            {
                'name'  : entry['name'],
                'key'   : k,
                'url'   : 'http://rdio.com%s' % entry['url']
            } 
                for k, entry in track_dict.items() 
        ]


class RdioTrack(_RdioObject, ResolverMediaItem):
    """
    Rdio track proxy
    """
    def __init__(self, data=None, rdio_id=None, rdio=None, maxLookupCalls=None):
        ResolverMediaItem.__init__(self, types=['track'], maxLookupCalls=maxLookupCalls)
        _RdioObject.__init__(self, data=data, rdio_id=rdio_id, rdio=rdio, extras='label, isCompilation')

    def _cleanName(self, rawName):
        return cleanTrackTitle(rawName)

    @lazyProperty
    def artists(self):
        result = {}
        try:
            result['name']  = self.data['artist']
            result['key']   = self.data['artistKey']
            result['url']   = 'http://rdio.com%s' % self.data['artistUrl']
            return [ result ]
        except Exception:
            return []

    @lazyProperty
    def albums(self):
        result = {}
        try:
            result['name']  = self.data['album']
            result['key']   = self.data['albumKey']
            result['url']   = 'http://rdio.com%s' % self.data['albumUrl']
            return [ result ]
        except Exception:
            return []

    @lazyProperty
    def length(self):
        return float(self.data['duration'])


def rdioJsonToResolverObject(rdioJson):
    t = rdioJson['type']
    if t == 't':
        return RdioTrack(data=rdioJson)
    elif t == 'a':
        return RdioAlbum(data=rdioJson)
    elif t == 'r':
        return RdioArtist(data=rdioJson)
    raise ValueError("bad type for Rdio data: %s" % data)

class RdioSearchAll(ResolverProxy, ResolverSearchAll):

    def __init__(self, data):
        target = rdioJsonToResolverObject(data)
        ResolverProxy.__init__(self, target)
        ResolverSearchAll.__init__(self)

class   RdioSource(GenericSource):
    """
    """
    def __init__(self):
        GenericSource.__init__(self, 'rdio', 
            groups=[
                'images',
                'albums',
                'tracks',
                'artists',
                'rdio_available',
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
    def __rdio(self):
        return globalRdio()

    def entityProxyFromKey(self, key, **kwargs):
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
        search = query.name
        try:
            if len(query.artists) > 0:
                search = '%s %s' % (search, query.artists[0]['name'])
        except:
            pass
        return self.generatorSource(self.__queryGen(
                query=search,
                types='Track',
                extras='',
                timeout=MERGE_TIMEOUT,
            ),
            constructor=RdioTrack)
    
    def albumSource(self, query):
        search = query.name
        try:
            if len(query.artists) > 0:
                search = '%s %s' % (search, query.artists[0]['name'])
        except:
            pass
        return self.generatorSource(self.__queryGen(
                query=search,
                types='Album',
                extras='label,isCompilation',
                timeout=MERGE_TIMEOUT,
            ),
            constructor=RdioAlbum)

    def artistSource(self, query):
        return self.generatorSource(self.__queryGen(
                query=query.name,
                types='Artist',
                extras='albumCount',
                timeout=MERGE_TIMEOUT,
            ),
            constructor=RdioArtist)

    def searchAllSource(self, query, timeout=None):
        if query.kinds is not None and len(query.kinds) > 0 and len(self.kinds.intersection(query.kinds)) == 0:
            logs.debug('Skipping %s (kinds: %s)' % (self.sourceName, query.kinds))
            return self.emptySource

        if query.types is not None and len(query.types) > 0 and len(self.types.intersection(query.types)) == 0:
            logs.debug('Skipping %s (types: %s)' % (self.sourceName, query.types))
            return self.emptySource

        logs.debug('Searching %s...' % self.sourceName)
        
        return self.generatorSource(self.__queryGen(
                query=query.query_string,
                types='Artist,Album,Track',
                extras='albumCount,label,isCompilation',
                timeout=MERGE_TIMEOUT,
            ),
            constructor=RdioSearchAll)
    
    def __queryGen(self, batches=(100,), timeout=None, **params):
        offset  = 0
        
        for batch in batches:
            response = self.__rdio.method('search',
                start=offset,
                count=batch,
                timeout=timeout,
                **params
            )
            if response['status'] == 'ok':
                entries = response['result']['results']
                for entry in entries:
                    yield entry
            else:
                return
            offset += batch

    class RequestFailedError(Exception):
        pass

    def searchLite(self, queryCategory, queryText, pool=None, timeout=None, coords=None, logRawResults=None):
        if queryCategory != 'music':
            raise Exception('Rdio only supports music!')
        response = self.__rdio.method('search',
                                      query=queryText,
                                      count=25,
                                      types='Artist,Album,Track',
                                      extras='albumCount,label,isCompilation', 
                                      priority='high',
                                      timeout=SEARCH_TIMEOUT)
        if response['status'] != 'ok':
            # TODO: Proper error handling here. Tracking of how often this happens.
            print "Rdio error; see response:"
            from pprint import pprint
            pprint(response)
            return []

        if logRawResults:
            logComponents = ['\n\n\nRDIO RAW RESULTS\nRDIO RAW RESULTS\nRDIO RAW RESULTS\n\n\n']
            logComponents.extend(['\n\n%s\n\n' % pformat(rawResult) for rawResult in response['result']['results']])
            logComponents.append('\n\n\nEND RDIO RAW RESULTS\n\n\n')
            logs.debug(''.join(logComponents))

        resolverObjects = [rdioJsonToResolverObject(result) for result in response['result']['results']]
        searchResults = scoreResultsWithBasicDropoffScoring(resolverObjects, sourceScore=0.7)
        for searchResult in searchResults:
            if isinstance(searchResult.resolverObject, RdioTrack):
                applyTrackTitleDataQualityTests(searchResult, queryText)
                adjustTrackRelevanceByQueryMatch(searchResult, queryText)
                augmentTrackDataQualityOnBasicAttributePresence(searchResult)
            elif isinstance(searchResult.resolverObject, RdioAlbum):
                applyAlbumTitleDataQualityTests(searchResult, queryText)
                adjustAlbumRelevanceByQueryMatch(searchResult, queryText)
                augmentAlbumDataQualityOnBasicAttributePresence(searchResult)
            elif isinstance(searchResult.resolverObject, RdioArtist):
                applyArtistTitleDataQualityTests(searchResult, queryText)
                adjustArtistRelevanceByQueryMatch(searchResult, queryText)
                augmentArtistDataQualityOnBasicAttributePresence(searchResult)
        sortByRelevance(searchResults)
        return searchResults

if __name__ == '__main__':
    demo(RdioSource(), 'Katy Perry')

