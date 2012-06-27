#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import sys, datetime, logs, gevent, utils
from api                        import Entity
from gevent.pool                import Pool
from resolve.iTunesSource       import iTunesSource
from resolve.AmazonSource       import AmazonSource
from resolve.RdioSource         import RdioSource
from resolve.SpotifySource      import SpotifySource
from resolve.TMDBSource         import TMDBSource
from resolve.TheTVDBSource      import TheTVDBSource
from resolve.GooglePlacesSource import GooglePlacesSource
from resolve.FactualSource      import FactualSource
from resolve.StampedSource      import StampedSource
from resolve.EntityProxyContainer   import EntityProxyContainer
from resolve.EntityProxySource  import EntityProxySource
from SearchResultDeduper        import SearchResultDeduper


def total_seconds(timedelta):
    return timedelta.seconds + (timedelta.microseconds / 1000000.0)


# Editable via command-line flags.
shouldLogSourceResults = False
shouldLogTiming = False
shouldLogClusters = False

def logClusterData(msg):
    if shouldLogClusters:
        logs.debug(msg)

def logTimingData(msg):
    if shouldLogTiming:
        logs.debug(msg)

def logSourceResultsData(msg):
    if shouldLogSourceResults:
        logs.debug(msg)


class EntitySearch(object):
    def __registerSource(self, source, **categoriesToPriorities):
        self.__all_sources.append(source)
        for (category, priority) in categoriesToPriorities.items():
            if category not in Entity.categories:
                raise Exception("unrecognized category: %s" % category)
            self.__categories_to_sources_and_priorities[category].append((source, priority))

    def __init__(self):
        allCategories = Entity.categories
        self.__all_sources = []
        # Within each category, we have a number of sources and each is assigned a priority. The priority is used to
        # determine how long to wait for results from that source.
        self.__categories_to_sources_and_priorities = {}
        for category in allCategories:
            self.__categories_to_sources_and_priorities[category] = []

        self.__registerSource(StampedSource(), music=10, film=10, book=10, app=10, place=10)
        self.__registerSource(iTunesSource(), music=10, film=10, book=3, app=10)
        # TODO: Enable film for Amazon. Amazon film results blend TV and movies and have better retrieval than
        # iTunes. On the other hand, they're pretty dreadful -- no clear distinction between TV and movies, no
        # clear distinction between individual movies and box sets, etc.
        self.__registerSource(AmazonSource(), music=5, book=10)
        self.__registerSource(GooglePlacesSource(), place=8)
        self.__registerSource(FactualSource(), place=8)
        self.__registerSource(TMDBSource(), film=8)
        self.__registerSource(TheTVDBSource(), film=8)
        self.__registerSource(RdioSource(), music=8)
        self.__registerSource(SpotifySource(), music=8)

    def __terminateWaiting(self, pool, start_time, category, resultsDict):
        sources_to_priorities = dict(self.__categories_to_sources_and_priorities[category])
        total_value_received = 0
        total_potential_value_outstanding = sum(sources_to_priorities.values())
        sources_seen = set()
        while True:
            try:
                elapsed_seconds = total_seconds(datetime.datetime.now() - start_time)

                if elapsed_seconds >= 20:
                    logs.warning('Search completely timed out at 20s!')
                    pool.kill()
                    return

                for (source, results) in resultsDict.items():
                    if source in sources_seen:
                        continue
                    logTimingData('JUST NOW SEEING SOURCE: ' + source.sourceName)
                    sources_seen.add(source)
                    # If a source returns at least 5 results, we assume we got a good result set from it. If it
                    # returns less, we're more inclined to wait for straggling sources.
                    total_value_received += sources_to_priorities[source] * min(5, len(results)) / 5.0
                    logTimingData('DECREMENTING OUTSTANDING BY ' + str(sources_to_priorities[source]) + ' FOR SOURCE ' + source.sourceName)
                    total_potential_value_outstanding -= sources_to_priorities[source]
                logTimingData('AT %f seconds elapsed, TOTAL VALUE RECEIVED IS %f, TOTAL OUTSTANDING IS %f' % (
                        elapsed_seconds, total_value_received, total_potential_value_outstanding
                    ))
            except Exception:
                logs.warning('TERMINATE_WARNING SHIT IS FUCKED')
                logs.report()
                raise

            if total_potential_value_outstanding <= 0:
                logTimingData('ALL SOURCES DONE')
                return

            if total_value_received:
                marginal_value_of_outstanding_sources = total_potential_value_outstanding / total_value_received
                # Comes out to:
                #   0.08 for 1s
                #   0.25 for 1.5s
                #   0.79 for 2s
                #   2.51 for 2.5s
                #   7.94 for 3s
                # So we'll ditch that 4th remaining source for music around 1.5s; we'll ditch the second source for
                # something like Places around 2s; we'll ditch any lingering source around 3s if we've received
                # anything.
                min_marginal_value = 10 ** (elapsed_seconds - 2.1)
                if min_marginal_value > marginal_value_of_outstanding_sources:
                    sources_not_seen = [
                        source.sourceName for source in sources_to_priorities.keys() if source not in sources_seen
                    ]
                    if sources_not_seen:
                        # This is interesting information whether we want the full timing data logged or not.
                        log_template = 'QUITTING EARLY: At %f second elapsed, bailing on sources [%s] because with ' + \
                            'value received %f, value outstanding %f, marginal value %f, min marginal value %f'
                        logs.debug(log_template % (
                            elapsed_seconds, ', '.join(sources_not_seen), total_value_received,
                            total_potential_value_outstanding, marginal_value_of_outstanding_sources, min_marginal_value
                        ))
                    pool.kill()
                    return

            gevent.sleep(0.01)

    def __searchSource(self, source, queryCategory, queryText, resultsDict, timesDict, **queryParams):
        # Note that the timing here is not 100% legit because gevent won't interrupt code except on I/O, but it's good
        # enough to give a solid idea.
        before = datetime.datetime.now()
        try:
            resultsDict[source] = source.searchLite(queryCategory, queryText, **queryParams)
        except:
            logs.report()
            resultsDict[source] = []
        after = datetime.datetime.now()
        timesDict[source] = after - before
        logs.debug("GOT RESULTS FROM SOURCE %s IN ELAPSED TIME %s -- COUNT: %d" % (
            source.sourceName, str(after - before), len(resultsDict.get(source, []))
        ))

    def search(self, category, text, timeout=None, limit=10, coords=None):
        if category not in Entity.categories:
            raise Exception("unrecognized category: (%s)" % category)

        start = datetime.datetime.now()
        results = {}
        times = {}
        pool = Pool(len(self.__categories_to_sources_and_priorities))
        for (source, priority) in self.__categories_to_sources_and_priorities[category]:
            # TODO: Handing the exact same timeout down to the inner call is probably wrong because we end up in this
            # situation where outer pools and inner pools are using the same timeout and possibly the outer pool will
            # nix the whole thing before the inner pool cancels out, which is what we'd prefer so that it's handled
            # more gracefully.
            pool.spawn(self.__searchSource, source, category, text, results, times, timeout=None, coords=coords)

        pool.spawn(self.__terminateWaiting, pool, datetime.datetime.now(), category, results)
        logTimingData("TIME CHECK ISSUED ALL QUERIES AT " + str(datetime.datetime.now()))
        pool.join()
        logTimingData("TIME CHECK GOT ALL RESPONSES AT " + str(datetime.datetime.now()))

        logTimingData('TIMES: ' + (', '.join(['%s took %s' % (source.sourceName, str(times[source])) for source in times])))
        for source in self.__all_sources:
            if source in results and results[source]:
                logSourceResultsData("\nRESULTS FROM SOURCE " + source.sourceName + " TIME ELAPSED: " + str(times[source]) + "\n\n")
                for result in results[source]:
                    logSourceResultsData(utils.normalize(repr(result)))
                    pass

        beforeDeduping = datetime.datetime.now()
        dedupedResults = SearchResultDeduper().dedupeResults(category, results.values())
        afterDeduping = datetime.datetime.now()
        logTimingData("DEDUPING TOOK " + str(afterDeduping - beforeDeduping))
        logTimingData("TIME CHECK DONE AT:" + str(datetime.datetime.now()))
        logTimingData("ELAPSED:" + str(afterDeduping - start))

        logClusterData("\n\nDEDUPED RESULTS\n\n")
        for dedupedResult in dedupedResults[:limit]:
            logClusterData("\n\n%s\n\n" % str(dedupedResult))

        return dedupedResults[:limit]


    def __getEntityIdForCluster(self, cluster):
        idsFromClusteredEntities = []
        for result in cluster.results:
            if result.resolverObject.source == 'stamped':
                idsFromClusteredEntities.append(result.resolverObject.key)

        fastResolvedIds = []
        for result in cluster.results:
            # TODO PRELAUNCH: MAKE SURE FAST RESOLUTION HANDLES TOMBSTONES PROPERLY
            entityId = self.__stampedSource.resolve_fast(result.resolverObject.source, result.resolverObject.key)
            if entityId:
                fastResolvedIds.append(entityId)

        allIds = idsFromClusteredEntities + fastResolvedIds
        if len(idsFromClusteredEntities) > 2:
            logs.warning('Search results directly clustered multiple StampedSource results: [%s]' %
                         ', '.join(str(entityId) for entityId in idsFromClusteredEntities))
        elif len(allIds) > 2:
            logs.warning('Search results indirectly clustered multiple entity IDs together: [%s]' %
                         ', '.join(str(entityId) for entityId in allIds))
        if not allIds:
            return None
        return allIds[0]


    def __proxyToEntity(self, cluster):
        # TODO PRELAUNCH: Resort cluster by data scoring, not relevancy/prominence.
        entityBuilder = EntityProxyContainer(cluster.results[0].resolverObject)
        for result in cluster.results[1:]:
            # TODO PRELAUNCH: Only use the best result from each source.
            entityBuilder.addSource(EntityProxySource(result.resolverObject))
        return entityBuilder.buildEntity()


    @utils.lazyProperty
    def __stampedSource(self):
        return StampedSource()


    def __buildEntity(self, entityId):
        # TODO PRELAUNCH: Should be able to avoid separate lookup here.
        proxy = self.__stampedSource.entityProxyFromKey(entityId)
        entity = EntityProxyContainer(proxy).buildEntity()
        entity.entity_id = entityId
        return entity


    def searchEntitiesAndClusters(self, category, text, timeout=3, limit=10, coords=None):
        clusters = self.search(category, text, timeout=timeout, limit=limit, coords=None)
        entityResults = []

        entityIdsToNewClusterIdxs = {}
        entitiesAndClusters = []
        for cluster in clusters:
            entityId = self.__getEntityIdForCluster(cluster)
            if not entityId:
                entitiesAndClusters.append((self.__proxyToEntity(cluster), cluster))
            # TODO PRELAUNCH: Make sure that the type we get from fast_resolve == the type we get from
            # StampedSourceObject.key, or else using these as keys in a map together won't work.
            elif entityId not in entityIdsToNewClusterIdxs:
                entityIdsToNewClusterIdxs[entityId] = len(entitiesAndClusters)
                entitiesAndClusters.append((self.__buildEntity(entityId), cluster))
            else:
                originalIndex = entityIdsToNewClusterIdxs[entityId]
                (_, originalCluster) = entitiesAndClusters[originalIndex]
                # We're not actually augmenting the result at all here; the result is the unadultered entity. We won't
                # show an entity augmented with other third-party IDs we've attached in search results because it will
                # create inconsistency for the entity show page and we don't know if they will definitely be attached.
                # The point of the grok is entirely to boost the rank of the cluster (and thus of the entity.)
                # TODO PRELAUNCH: Consider overriding this for sparse or user-created entities.
                # TODO: Debug check to see if the two are definitely not a match according to our clustering logic.
                originalCluster.grok(cluster)

        return entitiesAndClusters


    def searchEntities(self, *args, **kwargs):
        return [entity for entity, _ in self.searchEntitiesAndClusters(*args, **kwargs)]


from optparse import OptionParser
from libs.Geocoder import Geocoder

def main():
    usage = "Usage: %prog [options]"
    version = "%prog " + __version__
    parser = OptionParser(usage=usage, version=version)
    parser.add_option('--latlng', action='store', dest='latlng', default=None)
    parser.add_option('--address', action='store', dest='address', default=None)
    parser.add_option('-t', '--log_timing', action='store_true', dest='log_timing', default=False)
    parser.add_option('-r', '--log_source_results', action='store_true', dest='log_source_results', default=False)
    parser.add_option('-c', '--log_clusters', action='store_true', dest='log_clusters', default=False)
    (options, args) = parser.parse_args()

    global shouldLogSourceResults
    shouldLogSourceResults = options.log_source_results
    global shouldLogTiming
    shouldLogTiming = options.log_timing
    global shouldLogClusters
    shouldLogClusters = options.log_clusters


    queryParams = {}
    if options.latlng:
        queryParams['coords'] = options.latlng.split(',')
    elif options.address:
        queryParams['coords'] = Geocoder().addressToLatLng(options.address)

    if len(args) < 2 or args[0] not in Entity.categories:
        categories = '[ %s ]' % (', '.join(Entity.categories))
        print '\nUSAGE:\n\nEntitySearch.py <category> <search terms>\n\nwhere <category> is one of:', categories, '\n'
        return 1
    searcher = EntitySearch()
    results = searcher.searchEntities(args[0], ' '.join(args[1:]), **queryParams)
    for result in results:
        print "\n\n", result


if __name__ == '__main__':
    main()
