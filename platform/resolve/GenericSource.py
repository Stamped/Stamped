#!/usr/bin/env python
from __future__ import absolute_import

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'GenericSource', 'generatorSource', 'listSource', 'multipleSource' ]

import Globals

import logs, sys
from resolve.BasicSource                import BasicSource
from utils                      import lazyProperty
from gevent.pool                import Pool
from pprint                     import pprint, pformat
from abc                        import ABCMeta, abstractmethod
from resolve.Resolver                   import *
from resolve.ResolverObject             import *
from resolve.ASourceController          import *
from api.Schemas                import *
from resolve.EntityGroups               import *
from api.Entity                     import buildEntity

MERGE_TIMEOUT   = 60*60*5 # 5 hour timeout
SEARCH_TIMEOUT  = 10

def generatorSource(generator, constructor=None, unique=False, tolerant=False):
    if constructor is None:
        constructor = lambda x: x
    results = []
    if unique:
        value_set = set()
    def source(start, count):
        total = start + count
        while total > len(results):
            try:
                value = None
                if tolerant:
                    try:
                        value = constructor(generator.next())
                    except StopIteration:
                        raise
                    except Exception:
                        logs.report()
                else:
                    value = constructor(generator.next())
                if value is not None:
                    if unique:
                        if value not in value_set:
                            results.append(value)
                            value_set.add(value)
                    else:
                        results.append(value)
            except StopIteration:
                break

        result = results[start:]
        return result
    return source

def listSource(items, **kwargs):
    return generatorSource(iter(items), **kwargs)

def multipleSource(source_functions, initial_timeout=None, final_timeout=None, **kwargs):
    def gen():
        try:
            pool = Pool(len(source_functions))
            sources = []
            
            def _helper(source_function):
                source = source_function()
                if source is not None:
                    sources.append(source)
            
            for source_function in source_functions:
                pool.spawn(_helper, source_function)
            
            pool.join(timeout=initial_timeout)
            
            offset = 0
            found  = True
            
            while found:
                found = False
                
                for source in sources:
                    cur = source(offset, 1)
                    
                    for item in cur:
                        found = True
                        yield item
                
                offset += 1
        except GeneratorExit:
            pass
    return generatorSource(gen(),  **kwargs)

class GenericSource(BasicSource):
    """
    """
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        BasicSource.__init__(self, *args, **kwargs)
        self.addGroup(self.sourceName)

    @lazyProperty
    def resolver(self):
        return Resolver()

    @lazyProperty
    def stamped(self):
        from resolve import StampedSource
        return StampedSource.StampedSource()

    @abstractmethod
    def matchSource(self, query):
        pass

    def emptySource(self, start, count):
        return []

    def resolve(self, query, **options):
        return self.resolver.resolve(query, self.matchSource(query), **options)
    
    def generatorSource(self, generator, constructor=None, unique=False, tolerant=False):
        return generatorSource(generator, constructor=constructor, unique=unique, tolerant=tolerant)

    def entityProxyFromKey(self, key, **kwargs):
        raise NotImplementedError(str(type(self)))
    
    @property
    def idField(self):
        return "%s_id" % self.idName
    
    @property
    def urlField(self):
        return "%s_url" % self.idName
    
    @property 
    def idName(self):
        return self.sourceName

    def getId(self, entity):
        return getattr(entity.sources, self.idField)

    def enrichEntity(self, entity, groups, controller, decorations, timestamps):
        proxy = None
        results = None

        if self.getId(entity) is None and controller.shouldEnrich(self.idName, self.sourceName, entity):
            try:
                query = self.stamped.proxyFromEntity(entity)
                timestamps[self.idName] = controller.now
                results = self.resolve(query)
                if len(results) != 0:
                    best = results[0]
                    if best[0]['resolved']:
                        setattr(entity.sources, self.idField, best[1].key)            
                        if self.urlField is not None and best[1].url is not None:
                            setattr(entity.sources, self.urlField, best[1].url)
                        proxy = best[1]
            except ValueError:
                logs.report()

        source_id = self.getId(entity)
        if source_id is not None:
            if proxy is None:
                proxy = self.entityProxyFromKey(source_id, entity=entity)
            timestamps[self.idName] = controller.now
            for group in groups:
                if group.enrichEntityWithEntityProxy(entity, proxy):
                    timestamps[group.groupName] = controller.now

        # Haaaaaaaack.
        if results and self.sourceName != 'stamped':
            for result in results:
                if result[0]['resolved']:
                    entity.addThirdPartyId(self.sourceName, result[1].key)

        return True

