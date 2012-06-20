#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import sys, datetime
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
        before = datetime.datetime.now()
        resultsDict[source] = source.searchLite(queryCategory, queryText, **queryParams)
        after = datetime.datetime.now()
        timesDict[source] = after - before
        print "GOT RESULTS FROM SOURCE", source, "IN ELAPSED TIME", after - before, "COUNT", len(resultsDict[source])

    def search(self, category, text, timeout=None, **queryParams):
        if category not in Entity.categories:
            raise Exception("unrecognized category: (%s)" % category)

        start = datetime.datetime.now()
        results = {}
        times = {}
        pool = Pool(16)
        for source in self.__categories_to_sources[category]:
            # TODO: Handing the exact same timeout down to the inner call is probably wrong because we end up in this
            # situation where outer pools and inner pools are using the same timeout and possibly the outer pool will
            # nix the whole thing before the inner pool cancels out, which is what we'd prefer so that it's handled
            # more gracefully.
            pool.spawn(self.__searchSource, source, category, text, results, times, timeout=timeout, **queryParams)
        print "TIME CHECK ISSUED ALL QUERIES AT", datetime.datetime.now()
        pool.join(timeout=timeout)
        print "TIME CHECK GOT ALL RESPONSES AT", datetime.datetime.now()

        print "GOT RESULTS: ", (", ".join(['%d from %s' % (len(rList), source.sourceName) for (source, rList) in results.items()]))
        for source in self.__all_sources:
            if source in results and results[source]:
                print "\nRESULTS FROM SOURCE", source, "TIME ELAPSED:", times[source], "\n\n"
                for result in results[source]:
                    #print unicode(result).encode('utf-8'), "\n\n"
                    pass

        print "\n\n\n\nDEDUPING\n\n\n\n"
        beforeDeduping = datetime.datetime.now()
        dedupedResults = SearchResultDeduper().dedupeResults(category, results.values())
        afterDeduping = datetime.datetime.now()
        print "DEDUPING TOOK", afterDeduping - beforeDeduping
        print "TIME CHECK DONE AT", datetime.datetime.now()
        print "ELAPSED:", afterDeduping - start

        for dedupedResult in dedupedResults[:20]:
            print "\n\n"
            print dedupedResult
            print "\n\n"

        # TODO: Fast resolution against our database using all IDs!


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
    searcher.search(args[0], ' '.join(args[1:]), **queryParams)


if __name__ == '__main__':
    main()