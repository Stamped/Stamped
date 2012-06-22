#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import sys, datetime, logs, gevent
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
        logs.warning("RESTARTING")
        while True:
            elapsed_seconds = (datetime.datetime.now() - start_time).total_seconds()
            for (source, results) in resultsDict.items():
                if source in sources_seen:
                    continue
                logs.warning('JUST NOW SEEING SOURCE: ' + source.sourceName)
                sources_seen.add(source)
                logs.warning('SOURCES_SEEN IS ' + str([source for source in sources_seen]))
                # If a source returns at least 5 results, we assume we got a good result set from it. If it
                # returns less, we're more inclined to wait for straggling sources.
                total_value_received += sources_to_priorities[source] * min(5, len(results)) / 5.0
                total_potential_value_outstanding -= sources_to_priorities[source]
            logs.warning('AT %f seconds elapsed, TOTAL VALUE RECEIVED IS %f, TOTAL OUTSTANDING IS %f' % (
                    elapsed_seconds, total_value_received, total_potential_value_outstanding
                ))

            if total_potential_value_outstanding <= 0:
                logs.warning('ALL SOURCES DONE')
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
                        log_template = 'QUITTING EARLY: At %f second elapsed, bailing on sources [%s] because with ' + \
                            'value received %f, value outstanding %f, marginal value %f, min marginal value %f'
                        logs.warning(log_template % (
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

    def search(self, category, text, timeout=None, limit=10, **queryParams):
        logs.debug('In search')
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
            pool.spawn(self.__searchSource, source, category, text, results, times, timeout=None, **queryParams)

        pool.spawn(self.__terminateWaiting, pool, datetime.datetime.now(), category, results)
        logs.debug("TIME CHECK ISSUED ALL QUERIES AT " + str(datetime.datetime.now()))
        pool.join()
        logs.debug("TIME CHECK GOT ALL RESPONSES AT" + str(datetime.datetime.now()))

        logs.debug("GOT RESULTS: " + (", ".join(['%d from %s' % (len(rList), source.sourceName) for (source, rList) in results.items()])))
        logs.debug('TIMES: ' + (', '.join(['%s took %s' % (source.sourceName, str(times[source])) for source in times])))
        for source in self.__all_sources:
            if source in results and results[source]:
                logs.debug("\nRESULTS FROM SOURCE " + source.sourceName + " TIME ELAPSED: " + str(times[source]) + "\n\n")
                for result in results[source]:
                    #print unicode(result).encode('utf-8'), "\n\n"
                    pass

        logs.debug("DEDUPING")
        beforeDeduping = datetime.datetime.now()
        dedupedResults = SearchResultDeduper().dedupeResults(category, results.values())
        afterDeduping = datetime.datetime.now()
        logs.debug("DEDUPING TOOK " + str(afterDeduping - beforeDeduping))
        logs.debug("TIME CHECK DONE AT:" + str(datetime.datetime.now()))
        logs.debug("ELAPSED:" + str(afterDeduping - start))

        logs.debug("\n\nDEDUPED RESULTS\n\n")
        for dedupedResult in dedupedResults[:limit]:
            logs.debug("\n\n%s\n\n" % str(dedupedResult))

        return dedupedResults[:limit]


    def searchEntities(self, category, text, timeout=3, limit=10, queryLatLng=None, **queryParams):
        if queryLatLng:
            queryParams['queryLatLng'] = queryLatLng
        logs.debug('In searchEntities')
        stampedSource = StampedSource()
        clusters = self.search(category, text, timeout=timeout, limit=limit, **queryParams)
        entityResults = []
        for cluster in clusters:
            entityId = None
            for result in cluster.results:
                if result.resolverObject.source == 'stamped':
                    entityId = result.resolverObject.key
                    break

            results = cluster.results[:]
            results.sort(key = lambda result:result.score, reverse=True)
            for result in results:
                if entityId:
                    break
                proxy = result.resolverObject
                # TODO: Batch the database requests into one big OR query. Have appropriate handling for when we get
                # multiple Stamped IDs back.
                entityId = stampedSource.resolve_fast(proxy.source, proxy.key)
                # TODO: Incorporate data fullness here!

            if entityId:
                proxy = stampedSource.entityProxyFromKey(entityId)
                entity = EntityProxyContainer(proxy).buildEntity()
                # TODO: Somehow mark the entity to be enriched with these other IDs I've attached
                entity.entity_id = entityId
            else:
                entityBuilder = EntityProxyContainer(results[0].resolverObject)
                for result in results[1:]:
                    entityBuilder.addSource(EntityProxySource(result.resolverObject))
                entity = entityBuilder.buildEntity()

            entityResults.append(entity)

        return entityResults


from optparse import OptionParser
from libs.Geocoder import Geocoder

def main():
    usage = "Usage: %prog [options]"
    version = "%prog " + __version__
    parser = OptionParser(usage=usage, version=version)
    parser.add_option('--latlng', action='store', dest='latlng', default=None)
    parser.add_option('--address', action='store', dest='address', default=None)
    (options, args) = parser.parse_args()
    
    queryParams = {}
    if options.latlng:
        queryParams['queryLatLng'] = options.latlng.split(',')
    elif options.address:
        queryParams['queryLatLng'] = Geocoder().addressToLatLng(options.address)

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