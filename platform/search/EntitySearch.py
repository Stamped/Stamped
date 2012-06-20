#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import sys, datetime, logs
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
    def __registerSource(self, source, *categories):
        self.__all_sources.append(source)
        for category in categories:
            if category not in Entity.categories:
                raise Exception("unrecognized category: %s" % category)
            self.__categories_to_sources[category].append(source)

    def __init__(self):
        allCategories = Entity.categories
        self.__all_sources = []
        self.__categories_to_sources = {}
        for category in allCategories:
            self.__categories_to_sources[category] = []

        #self.__registerSource(StampedSource(), allCategories)
        self.__registerSource(iTunesSource(), 'music', 'film', 'book', 'app')
        # TODO: Enable film for Amazon. Amazon film results blend TV and movies and have better retrieval than
        # iTunes. On the other hand, they're pretty dreadful -- no clear distinction between TV and movies, no
        # clear distinction between individual movies and box sets, etc.
        self.__registerSource(AmazonSource(), 'music' ,'book')
        self.__registerSource(GooglePlacesSource(), 'place')
        self.__registerSource(FactualSource(), 'place')
        self.__registerSource(TMDBSource(), 'film')
        self.__registerSource(TheTVDBSource(), 'film')
        self.__registerSource(RdioSource(), 'music')
        self.__registerSource(SpotifySource(), 'music')

    def __searchSource(self, source, queryCategory, queryText, resultsDict, timesDict, **queryParams):
        # Note that the timing here is not 100% legit because gevent won't interrupt code except on I/O, but it's good
        # enough to give a solid idea.
        logs.debug("DEBUG DEBUG DEBUG OK ABOUT TO SEARCH SOURCE " + source.sourceName)
        before = datetime.datetime.now()
        try:
            logs.debug('DEBUG DEBUG DEBUG Searching source: ' + source.sourceName)
            resultsDict[source] = source.searchLite(queryCategory, queryText, **queryParams)
            logs.debug('DEBUG DEBUG DEBUG Done searching source: ' + source.sourceName)
        except:
            logs.report()
        after = datetime.datetime.now()
        timesDict[source] = after - before
        logs.debug("GOT RESULTS FROM SOURCE %s IN ELAPSED TIME %s -- COUNT: %d" % (
            source, str(after - before), len(resultsDict[source])
        ))

    def search(self, category, text, timeout=None, limit=10, **queryParams):
        logs.debug('In search')
        if category not in Entity.categories:
            raise Exception("unrecognized category: (%s)" % category)

        start = datetime.datetime.now()
        results = {}
        times = {}
        pool = Pool(len(self.__categories_to_sources))
        logs.debug('DEBUG DEBUG DEBUG Category is: ' + category)
        logs.debug('DEBUG DEBUG DEBUG Num sources: ' + str(len(self.__categories_to_sources[category])))
        for source in self.__categories_to_sources[category]:
            # TODO: Handing the exact same timeout down to the inner call is probably wrong because we end up in this
            # situation where outer pools and inner pools are using the same timeout and possibly the outer pool will
            # nix the whole thing before the inner pool cancels out, which is what we'd prefer so that it's handled
            # more gracefully.
            logs.debug('DEBUG DEBUG DEBUG NOW SPAWNING FOR SOURCE ' + source.sourceName)
            pool.spawn(self.__searchSource, source, category, text, results, times, timeout=timeout, **queryParams)
            logs.debug('DEBUG DEBUG DEBUG DONE SPAWNING FOR SOURCE ' + source.sourceName)
        logs.debug("TIME CHECK ISSUED ALL QUERIES AT " + str(datetime.datetime.now()))
        pool.join(timeout=timeout)
        logs.debug("TIME CHECK GOT ALL RESPONSES AT" + str(datetime.datetime.now()))

        logs.debug("GOT RESULTS: " + (", ".join(['%d from %s' % (len(rList), source.sourceName) for (source, rList) in results.items()])))
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


    def searchEntities(self, category, text, timeout=None, limit=10, **queryParams):
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