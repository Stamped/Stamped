#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'TheTVDBSource', 'TheTVDBArtist', 'TheTVDBAlbum', 'TheTVDBTrack', 'TheTVDBSearchAll' ]

import Globals
from logs import report

try:
    import logs, utils
    from Resolver                   import *
    from ResolverObject             import *
    from libs.TheTVDB               import TheTVDB, globalTheTVDB
    from GenericSource              import GenericSource
    from utils                      import lazyProperty
    from pprint                     import pformat
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
    def name(self):
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
        try:
            return self.data.genres
        except Exception:
            return []
    
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
        try:
            if key.startswith('t'):
                return TheTVDBTrack(rdio_id=key)
            if key.startswith('a'):
                return TheTVDBAlbum(rdio_id=key)
            if key.startswith('r'):
                return TheTVDBArtist(rdio_id=key)
            raise KeyError
        except KeyError:
            logs.warning('Unable to find TVDB item for key: %s' % key)
            raise
        
        return None
    
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
                                    constructor=TheTVDBTrack)
    
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
    
    def __queryGen(self, batches=(100,), **params):
        def gen():
            try:
                batches = [100]
                offset  = 0
                
                results = self.__thetvdb.search(transform=True, detailed=True, **params)
                
                for result in results:
                    yield result
            except GeneratorExit:
                pass
        
        return gen()

    def searchLite(self, queryCategory, queryText):
        if queryCategory != 'film':
            raise NotImplementedError()
        # Ugh. Why are we using entities?
        entities = self.__thetvdb.search(queryText, transform=True, detailed=False)
        results = [TheTVDBShow(data=entity) for entity in entities]
        # TheTVDB has a higher source score than TMDB because it is strict with its retrieval. If you don't match
        # closely, it won't return anything.
        return scoreResultsWithBasicDropoffScoring(results, sourceScore=1.1)

if __name__ == '__main__':
    demo(TheTVDBSource(), 'Archer')

