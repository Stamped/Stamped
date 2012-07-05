#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'TheTVDBSource', 'TheTVDBShow', 'TheTVDBSearchAll' ]

import Globals
from logs import report

try:
    import logs, utils
    from Resolver                   import *
    from ResolverObject             import *
    from TitleUtils                 import *
    from libs.TheTVDB               import TheTVDB, globalTheTVDB
    from GenericSource              import GenericSource
    from utils                      import lazyProperty
    from pprint                     import pformat, pprint
    from search.ScoringUtils        import *
except:
    report()
    raise


class _TheTVDBObject(object):
    """
    Abstract superclass (mixin) for TheTVDB objects.
    
    _TheTVDBObjects can be instatiated with either the thetvdb_id or the tvdb data for an entity.
    If both are provided, they must match. extras may be used to retrieve additional data
    when instantiating an object using only its id.
    
    Attributes:
    
    data    - the type-specific thetvdb data for the entity
    thetvdb - an instance of TheTVDB (API proxy)
    """
    
    def __init__(self, data=None, thetvdb_id=None, thetvdb=None, extras=''):
        if thetvdb is None:
            thetvdb = globalTheTVDB()
        
        if data is None:
            if thetvdb_id is None:
                raise ValueError('data or thetvdb_id must not be None')
            
            try:
                data = thetvdb.lookup(thetvdb_id)
            except KeyError:
                raise ValueError('bad thetvdb_id')
        elif thetvdb_id is not None:
            if thetvdb_id != data.sources.thetvdb_id:
                raise ValueError('thetvdb_id does not match data["key"]')
        
        self.__thetvdb = thetvdb
        self.__data    = data
    
    @property
    def thetvdb(self):
        return self.__thetvdb
    
    @property
    def data(self):
        return self.__data
    
    @lazyProperty
    def raw_name(self):
        return self.data.title
    
    @property 
    def source(self):
        return "thetvdb"
    
    def __repr__(self):
        return pformat( self.data )

class TheTVDBShow(_TheTVDBObject, ResolverMediaCollection):
    """
        TheTVDB show proxy
    """
    
    def __init__(self, data=None, thetvdb_id=None, thetvdb=None):
        _TheTVDBObject.__init__(self, data=data, thetvdb_id=thetvdb_id, thetvdb=thetvdb)
        ResolverMediaCollection.__init__(self, types=['tv'])

    def _cleanName(self, rawName):
        return cleanTvTitle(rawName)

    @lazyProperty
    def key(self):
        return self.data.sources.thetvdb_id
    
    @lazyProperty
    def cast(self):
        if self.data.cast is None:
            return []
        return map(lambda x: { 'name' : x.title }, self.data.cast)

    @lazyProperty
    def directors(self):
        return []
    
    @lazyProperty
    def date(self):
        return self.data.release_date
    
    @lazyProperty
    def seasons(self):
        return -1
    
    @lazyProperty
    def networks(self):
        if self.data.networks is None:
            return []
        return map(lambda x: { 'name' : x.title }, self.data.networks)
    
    @lazyProperty 
    def genres(self):
        if self.data.genres is None:
            return []
        return self.data.genres

    @lazyProperty
    def description(self):
        try:
            return self.data.desc
        except Exception:
            return ''
    
class TheTVDBSearchAll(ResolverProxy, ResolverSearchAll):

    def __init__(self, data):
        target = TheTVDBShow(data)
        
        ResolverProxy.__init__(self, target)
        ResolverSearchAll.__init__(self)

class TheTVDBSource(GenericSource):
    
    def __init__(self):
        GenericSource.__init__(self, 'thetvdb', 
            groups=[
                'genres',
                'desc',
                'cast', 
                'imdb', 
                'networks', 
            ],
            kinds=[
                'media_collection',
            ],
            types=[
                'tv',
            ]
        )
    
    @lazyProperty
    def __thetvdb(self):
        return globalTheTVDB()
    
    def entityProxyFromKey(self, key, **kwargs):
        return TheTVDBShow(thetvdb_id=key)

    def entityProxyFromData(self, data):
        return TheTVDBSource(data=data)
    
    def enrichEntityWithEntityProxy(self, proxy, entity, controller=None, decorations=None, timestamps=None):
        GenericSource.enrichEntityWithEntityProxy(self, proxy, entity, controller, decorations, timestamps)
        entity.sources.thetvdb_id = proxy.key
        return True
    
    def matchSource(self, query):
        if query.kind == 'search':
            return self.searchAllSource(query)

        if query.isType('tv'):
            return self.tvSource(query)
        
        return self.emptySource
    
    def tvSource(self, query):
        return self.generatorSource(self.__queryGen(query=query.name), 
                                    constructor=TheTVDBShow)
    
    def searchAllSource(self, query, timeout=None):
        if query.kinds is not None and len(query.kinds) > 0 and len(self.kinds.intersection(query.kinds)) == 0:
            logs.info('Skipping %s (kinds: %s)' % (self.sourceName, query.kinds))
            return self.emptySource

        if query.types is not None and len(query.types) > 0 and len(self.types.intersection(query.types)) == 0:
            logs.info('Skipping %s (types: %s)' % (self.sourceName, query.types))
            return self.emptySource

        logs.info('Searching %s...' % self.sourceName)
        
        return self.generatorSource(self.__queryGen(query=query.query_string),
                                    constructor=TheTVDBSearchAll)
    
    def __queryGen(self, **params):
        results = self.__thetvdb.search(transform=True, detailed=True, **params)
        for result in results:
            yield result

    def searchLite(self, queryCategory, queryText, timeout=None, coords=None, logRawResults=False):
        # TODO: USE TIMEOUT.
        if queryCategory != 'film':
            raise NotImplementedError()
        # Ugh. Why are we using entities?
        rawResults = self.__thetvdb.search(queryText, transform=True, detailed=False)
        if logRawResults:
            logComponents = ['\n\n\nTheTVDB RAW RESULTS\nTheTVDB RAW RESULTS\nTheTVDB RAW RESULTS\n\n\n']
            for rawResult in rawResults:
                logComponents.extend(['\n\n', pformat(rawResult), '\n\n'])
            logComponents.append('\n\n\nEND TheTVDB RAW RESULTS\n\n\n')
            logs.debug(''.join(logComponents))

        resolverObjects = [TheTVDBShow(data=rawResult) for rawResult in rawResults]
        # TheTVDB has a higher source score than TheTVDB because it is strict with its retrieval. If you don't match
        # closely, it won't return anything.
        searchResults = scoreResultsWithBasicDropoffScoring(resolverObjects, sourceScore=1.1)
        for searchResult in searchResults:
            applyTvTitleDataQualityTests(searchResult, queryText)
            adjustTvRelevanceByQueryMatch(searchResult, queryText)
        return searchResults

if __name__ == '__main__':
    demo(TheTVDBSource(), 'Archer')

