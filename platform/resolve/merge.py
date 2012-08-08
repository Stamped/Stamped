#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

import logs

from utils import lazyProperty, LoggingThreadPool

from crawler.RssFeedScraper import RssFeedScraper

from resolve import FullResolveContainer, EntityProxyContainer
from resolve.EntitySource import EntitySource
from resolve.EntityProxySource import EntityProxySource
from resolve.BasicSourceContainer import BasicSourceContainer
from resolve.AmazonSource import AmazonSource
from resolve.FactualSource import FactualSource
from resolve.GooglePlacesSource import GooglePlacesSource
from resolve.iTunesSource import iTunesSource
from resolve.NetflixSource import NetflixSource
from resolve.RdioSource import RdioSource
from resolve.SpotifySource import SpotifySource
from resolve.TMDBSource import TMDBSource
from resolve.TheTVDBSource import TheTVDBSource
from resolve.StampedSource import StampedSource
from resolve.EntityProxySource import EntityProxySource




class Merge(object):

    @lazyProperty
    def __full_resolve(self):
        return FullResolveContainer.FullResolveContainer()

    def __handleDecorations(self, entity, decorations):
        for k,v in decorations.items():
            ### TODO: decorations returned as dict, not schema. Fix?
            if k == 'menu':
                try:
                    self._menuDB.update(v)
                except Exception:
                    logs.warning('Menu enrichment failed')
                    report()

    def convertSearchId(self, search_id):
        temp_id_prefix = 'T_'
        if not search_id.startswith(temp_id_prefix):
            # already a valid entity id
            return search_id

        # TODO: This code should be moved into a common location with BasicEntity.search_id
        id_components = search_id[len(temp_id_prefix):].split('____')

        sources = {
            'amazon':       AmazonSource,
            'factual':      FactualSource,
            'googleplaces': GooglePlacesSource,
            'itunes':       iTunesSource,
            'rdio':         RdioSource,
            'spotify':      SpotifySource,
            'tmdb':         TMDBSource,
            'thetvdb':      TheTVDBSource,
            'netflix':      NetflixSource,
        }

        sourceAndKeyRe = re.compile('^([A-Z]+)_([\w+-:/]+)$')
        sourcesAndKeys = []
        for component in id_components:
            match = sourceAndKeyRe.match(component)
            if not match:
                logs.warning('Unable to parse search ID component:' + component)
            else:
                sourcesAndKeys.append(match.groups())
        if not sourcesAndKeys:
            logs.warning('Unable to extract and third-party ID from composite search ID: ' + search_id)
            raise StampedUnavailableError("Entity not found")

        stamped = StampedSource()
        fast_resolve_results = stamped.resolve_fast_batch(sourcesAndKeys)
        entity_ids = filter(None, fast_resolve_results)
        if len(entity_ids):
            entity_id = entity_ids[0]
        else:
            entity_id = None

        proxies = []
        if not entity_id:
            seenSourceNames = set()
            entity_ids = []
            pool = LoggingThreadPool(len(sources))
            for sourceIdentifier, key in sourcesAndKeys:
                if sourceIdentifier in seenSourceNames:
                    continue
                seenSourceNames.add(sourceIdentifier)

                def loadProxy(sourceIdentifier, key):
                    source = sources[sourceIdentifier.lower()]()
                    try:
                        proxy = source.entityProxyFromKey(key)
                        proxies.append(proxy)
                        if len(proxies) == 1:
                            # This is the first proxy, so we'll try to resolve against Stamped.
                            results = stamped.resolve(proxy)

                            if len(results) > 0 and results[0][0]['resolved']:
                                # We were able to find a match in the Stamped DB.
                                entity_ids.append(results[0][1].key)
                                pool.kill()

                    except KeyError:
                        logs.warning('Failed to load key %s from source %s; exception body:\n%s' %
                                     (key, sourceIdentifier, traceback.format_exc()))

                pool.spawn(loadProxy, sourceIdentifier, key)

            MAX_LOOKUP_TIME=2.5
            pool.join(timeout=MAX_LOOKUP_TIME)
            if entity_ids:
                entity_id = entity_ids[0]

        if not entity_id and not proxies:
            logs.warning('Completely unable to create entity from search ID: ' + search_id)
            raise StampedUnavailableError("Entity not found")

        if entity_id is None:
            entity = EntityProxyContainer.EntityProxyContainer().addAllProxies(proxies).buildEntity()
            entity.third_party_ids = id_components

            entity = self._entityDB.addEntity(entity)
            entity_id = entity.entity_id

        # Enrich and merge entity asynchronously
        self.mergeEntityId(entity_id)

        logs.info('Converted search_id (%s) to entity_id (%s)' % (search_id, entity_id))
        return entity_id

    
    def mergeEntity(self, entity):
        logs.info('Merge Entity: "%s"' % entity.title)

        try:
            self.call_task(self.mergeEntityAsync, {'entityDict': entity.dataExport()}, fallback=False, queue='enrich')
        except Exception as e:
            pass

    def mergeEntityAsync(self, entityDict):
        self._mergeEntity(Entity.buildEntity(entityDict))

    def mergeEntityId(self, entityId):
        logs.info('Merge EntityId: %s' % entityId)

        try:
            self.call_task(self.mergeEntityIdAsync, {'entityId': entityId}, fallback=False, queue='enrich')
        except Exception as e:
            pass

    def mergeEntityIdAsync(self, entityId):
        try:
            entity = self._entityDB.getEntity(entityId)
        except StampedDocumentNotFoundError:
            logs.warning("Entity not found: %s" % entityId)
            return
        self._mergeEntity(entity)

    def _mergeEntity(self, entity):
        """Enriches the entity and possibly follow any links it may have.
        """
        persisted = set()
        entity = self._enrichAndPersistEntity(entity, persisted)
        self._followOutLinks(entity, persisted, 0)
        return entity

    def _enrichAndPersistEntity(self, entity, persisted):
        if entity.entity_id in persisted:
            return entity
        logs.info('Merge Entity Async: "%s" (id = %s)' % (entity.title, entity.entity_id))
        entity, modified = self._resolveEntity(entity)
        logs.info('Modified: ' + str(modified))
        modified = self._resolveRelatedEntities(entity) or modified

        if modified:
            if entity.entity_id is None:
                entity = self._entityDB.addEntity(entity)
            else:
                entity = self._entityDB.updateEntity(entity)
        persisted.add(entity.entity_id)
        return entity

    def _resolveEntity(self, entity):
        def _getSuccessor(tombstoneId):
            logs.info("Get successor: %s" % tombstoneId)
            successor_id = tombstoneId
            successor    = self._entityDB.getEntity(successor_id)
            assert successor is not None and successor.entity_id == successor_id

            # TODO: Because we create a new FullResolveContainer() here instead of using self.__full_resolve, we are not
            # reading from or writing to  the joint history about what sources have failed recently and are still
            # cooling down.
            merger = FullResolveContainer.FullResolveContainer()
            merger.addSource(EntitySource(entity, merger.groups))
            successor_decorations = {}
            modified_successor = merger.enrichEntity(successor, successor_decorations)
            self.__handleDecorations(successor, successor_decorations)

            return successor, modified_successor

        try:
            # TEMP: Short circuit if user-generated
            if entity.sources.user_generated_id is not None:
                return entity, False

            # Short circuit if entity is already tombstoned
            if entity.sources.tombstone_id is not None:
                successor, modified_successor = _getSuccessor(entity.sources.tombstone_id)
                logs.info("Entity (%s) already tombstoned (%s)" % (entity.entity_id, successor.entity_id))
                return successor, modified_successor

            # Enrich entity
            decorations = {}
            modified    = self.__full_resolve.enrichEntity(entity, decorations, max_iterations=4)

            # Return successor if entity is tombstoned
            if entity.sources.tombstone_id is not None and entity.sources.tombstone_id != '': # HACK: Why is tombstone_id == ''?
                successor, modified_successor = _getSuccessor(entity.sources.tombstone_id)

                if entity.entity_id is not None:
                    self._entityDB.updateEntity(entity)

                logs.info("Merged entity (%s) with entity %s" % (entity.entity_id, successor.entity_id))
                return successor, modified_successor

            self.__handleDecorations(entity, decorations)

            return entity, modified

        except Exception:
            report()
            raise

    def _resolveRelatedEntities(self, entity):
        def _resolveStubList(entity, attr):
            stubList = getattr(entity, attr)
            if not stubList:
                return False

            resolvedList = []
            stubsModified = False

            for stub in stubList:
                stubId = stub.entity_id
                resolved = self._resolveStub(stub, True)
                if resolved is None:
                    resolvedList.append(stub)
                else:
                    resolvedList.append(resolved.minimize())
                    if stubId != resolved.entity_id:
                        stubsModified = True

            if entity.isType('artist'):
                # Do a quick dedupe of songs in case the same song appears in different albums.
                seenTitles = set()
                dedupedList = []
                for resolved in resolvedList:
                    if resolved.title not in seenTitles:
                        dedupedList.append(resolved)
                        seenTitles.add(resolved.title)
                resolvedList = dedupedList[:20]
            setattr(entity, attr, resolvedList)
            return stubsModified

        return self._iterateOutLinks(entity, _resolveStubList)

    def _shouldFollowLink(self, entity, attribute, depth):
        if attribute == 'albums':
            return False
        if entity.isType('album'):
            return attribute == 'tracks'
        if entity.isType('artist'):
            return True
        return depth == 0

    def _followOutLinks(self, entity, persisted, depth):
        def followStubList(entity, attr):
            if not self._shouldFollowLink(entity, attr, depth):
                return
            stubList = getattr(entity, attr)
            if not stubList:
                return

            modified = False
            visitedStubs = []
            mergedEntities = []
            for stub in stubList:
                resolvedFull = self._resolveStub(stub, False)
                if resolvedFull is None:
                    modified = True
                    logs.warning('stub resolution failed: %s' % stub)
                    if attr == 'artists':
                        visitedStubs.append(stub)
                else:
                    mergedEntity = self._enrichAndPersistEntity(resolvedFull, persisted)
                    mergedEntities.append(mergedEntity)
                    visitedStubs.append(mergedEntity.minimize())
                    modified = modified or (visitedStubs[-1] != stub)

            seenLinks = set()
            dedupedList = []
            for resolved in visitedStubs:
                if not resolved.entity_id:
                    dedupedList.append(resolved)
                elif resolved.entity_id not in seenLinks:
                    dedupedList.append(resolved)
                    seenLinks.add(resolved.entity_id)
            setattr(entity, attr, dedupedList)
            if modified:
                self._entityDB.updateEntity(entity)

            for mergedEntity in mergedEntities:
                self._followOutLinks(mergedEntity, persisted, depth+1)
        self._iterateOutLinks(entity, followStubList)

    def _resolveStub(self, stub, quickResolveOnly):
        """Tries to return either an existing StampedSource entity or a third-party source entity proxy.

        Tries to fast resolve Stamped DB using existing third-party source IDs.
        Failing that (for one source at a time, not for all sources) tries to use standard resolution against
            StampedSource. (TODO: probably worth trying fast_resolve against all sources first, before trying
            falling back?)
        Failing that, just returns an entity proxy using one of the third-party sources for which we found an ID,
            if there were any.
        If none of this works, returns None
        """

        musicSources = {
            'itunes':       iTunesSource,
            'rdio':         RdioSource,
            'spotify':      SpotifySource,
            'amazon':       AmazonSource,
        }

        source          = None
        source_id       = None
        entity_id       = None
        proxy           = None

        stampedSource   = StampedSource(stamped_api=self)

        if stub.entity_id is not None and not stub.entity_id.startswith('T_'):
            entity_id = stub.entity_id
        else:
            # TODO GEOFF FUCK FUCK FUCK: Use third_party_ids here, and resolve_fast_batch!
            for sourceName in musicSources:
                try:
                    if getattr(stub.sources, '%s_id' % sourceName, None) is not None:
                        source = musicSources[sourceName]()
                        source_id = getattr(stub.sources, '%s_id' % sourceName)
                        # Attempt to resolve against the Stamped DB (quick)
                        entity_id = stampedSource.resolve_fast(sourceName, source_id)
                        if entity_id is None and not quickResolveOnly:
                            # Attempt to resolve against the Stamped DB (full)
                            proxy = source.entityProxyFromKey(source_id, entity=stub)
                            results = stampedSource.resolve(proxy)
                            if len(results) > 0 and results[0][0]['resolved']:
                                entity_id = results[0][1].key
                        break
                except Exception as e:
                    logs.info('Threw exception while trying to resolve source %s: %s' % (sourceName, e.message))
                    continue
        if entity_id is not None:
            try:
                entity = self._entityDB.getEntity(entity_id)
            except StampedDocumentNotFoundError:
                logs.warning("Entity id is invalid: %s" % entity_id)
                entity_id = None

        if entity_id is not None:
            pass
        elif source_id is not None and proxy is not None:
            entity = EntityProxyContainer.EntityProxyContainer().addProxy(proxy).buildEntity()
        else:
            return None

        if entity.kind != stub.kind:
            logs.info('Confused and dazed. Stub and result are different kinds: ' + str(stub))
            return None
        return entity

    def _iterateOutLinks(self, entity, func):
        modified = False
        if entity.isType('album'):
            modified = func(entity, 'artists') or modified
            modified = func(entity, 'tracks') or modified
        elif entity.isType('artist'):
            modified = func(entity, 'albums') or modified
            modified = func(entity, 'tracks') or modified
        elif entity.isType('track'):
            modified = func(entity, 'artists') or modified
            modified = func(entity, 'albums') or modified

        return modified


    def crawlExternalSourcesAsync(self):
        stampedSource = StampedSource(stamped_api=self)
        for proxy in RssFeedScraper().fetchSources():
            self.mergeProxyIntoDb(proxy, stampedSource)

    def mergeProxyIntoDb(self, proxy, stampedSource):
        entity_id = stampedSource.resolve_fast(proxy.source, proxy.key)

        if entity_id is None:
            results = stampedSource.resolve(proxy)
            if len(results) > 0 and results[0][0]['resolved']:
                entity_id = results[0][1].key

        # The crawled sources are usually readonly sources, such as a scraped website or RSS feed.
        # We therefore can't rely on full enrichment to correctly pick up the data from those
        # sources. That is why we make sure we incorporate the data from the proxy here, either by
        # building a new entity or enriching an existing one.
        if entity_id is None:
            entity = EntityProxyContainer.EntityProxyContainer().addProxy(proxy).buildEntity()
        else:
            entity = self._entityDB.getEntity(entity_id)
            sourceContainer = BasicSourceContainer()
            sourceContainer.addSource(EntityProxySource(proxy))
            sourceContainer.enrichEntity(entity, {})
        self.mergeEntity(entity)
