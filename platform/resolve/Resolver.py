#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [
    'Resolver',
    'ResolverProxy',
    'demo',
]

import Globals
from logs import report

try:
    import utils, re, string, sys, traceback
    import logs, sys, math
    import unicodedata
    # from EntityProxyContainer import EntityProxyContainer
    
    from resolve.BasicSource                import BasicSource
    from utils                      import lazyProperty
    from pprint                     import pprint, pformat
    from gevent.pool                import Pool
    from abc                        import ABCMeta, abstractmethod, abstractproperty
    from libs.LibUtils              import parseDateString
    from datetime                   import datetime
    from difflib                    import SequenceMatcher
    from resolve.ResolverObject             import *
    from resolve.EntityProxyComparator      import *

    # TODO FUCK FUCK FUCK SHOULD REALLY NOT NEED TO PULL FROM SEARCH, OR USE SEARCHRESULT AT ALL
    from search.SearchResult import SearchResult
    from search.DataQualityUtils import *
    from resolve.TitleUtils import *
except:
    report()
    raise

useComparators = True

class ResolverProxy(object):

    def __init__(self, target):
        self.__target = target

    @property
    def target(self):
        return self.__target

    @lazyProperty
    def url(self):
        return self.target.url

    @lazyProperty
    def key(self):
        return self.target.key

    @property 
    def source(self):
        return self.target.source

    def __repr__(self):
        try:
            return "ResolverProxy:%s\n%s" % (str(self.target), str(self.target.keywords))
        except:
            return "ResolverProxy"

    @property
    def keywords(self):
        return self.target.keywords
    
    @property
    def name(self):
        return self.target.name

    @property 
    def priority(self):
        return self.target.priority

    @property 
    def related_terms(self):
        return self.target.related_terms

    @property
    def coordinates(self):
        return self.target.coordinates

    @property
    def address(self):
        return self.target.address

    @property
    def image(self):
        return self.target.image

    @property
    def release_date(self):
        return self.target.release_date


##
# Main Resolver class
##

class Resolver(object):
    """
    The central resolve utility class

    The Resolver class embodies the algorithms for many types of generic and fuzzy comparisons,
    as well as several high-level resolve methods for the specific object types defined in this module.

    Most Resolver methods use an options dict to customize behavior but
    Methods with public names can be safely overriden (assuming they present the same interface) in 
    subclasses to customize behavior.

    Resolver objects are virtually stateless so many can be instatiated or a few can be shared.
    """
    def __init__(self,verbose=False):
        self.__verbose = verbose
    
    @property 
    def verbose(self):
        return self.__verbose

    def checkWithComparator(self, comparator, results, query, match, options, order, subcat):
        search_result_fuckfuckfuck_hack = SearchResult(match)
        if subcat == 'artist':
            augmentArtistDataQualityOnBasicAttributePresence(search_result_fuckfuckfuck_hack)
            applyArtistTitleDataQualityTests(search_result_fuckfuckfuck_hack, query.name)
        elif subcat == 'album':
            augmentAlbumDataQualityOnBasicAttributePresence(search_result_fuckfuckfuck_hack)
            applyAlbumTitleDataQualityTests(search_result_fuckfuckfuck_hack, query.name)
        elif subcat == 'track':
            augmentTrackDataQualityOnBasicAttributePresence(search_result_fuckfuckfuck_hack)
            applyTrackTitleDataQualityTests(search_result_fuckfuckfuck_hack, query.name)
        elif subcat == 'tv':
            augmentTvDataQualityOnBasicAttributePresence(search_result_fuckfuckfuck_hack)
            applyTvTitleDataQualityTests(search_result_fuckfuckfuck_hack, query.name)
        elif subcat == 'movie':
            augmentMovieDataQualityOnBasicAttributePresence(search_result_fuckfuckfuck_hack)
            applyMovieTitleDataQualityTests(search_result_fuckfuckfuck_hack, query.name)
        elif subcat == 'book':
            augmentBookDataQualityOnBasicAttributePresence(search_result_fuckfuckfuck_hack)
            applyBookTitleDataQualityTests(search_result_fuckfuckfuck_hack, query.name)
        elif subcat == 'place':
            augmentPlaceDataQualityOnBasicAttributePresence(search_result_fuckfuckfuck_hack)
            applyPlaceTitleDataQualityTests(search_result_fuckfuckfuck_hack, query.name)
        elif subcat == 'app':
            augmentAppDataQualityOnBasicAttributePresence(search_result_fuckfuckfuck_hack)
            applyAppTitleDataQualityTests(search_result_fuckfuckfuck_hack, query.name)

        comparison_result = search_result_fuckfuckfuck_hack.dataQuality > 0.6 and \
                            comparator.compare_proxies(query, match).is_match()

        similarity = 100 if comparison_result else 0
        similarities = {'total': similarity}

        result = (similarities, match)
        results.append(result)
        options['callback'](result, order)

    def checkPerson(self, results, query, match, options, order):
        types = self.__typesIntersection(query, match)
        if 'artist' in types:
            self.checkWithComparator(ArtistEntityProxyComparator, results, query, match, options, order, 'artist')
            return

    def checkPlace(self, results, query, match, options, order):
        self.checkWithComparator(PlaceEntityProxyComparator, results, query, match, options, order, 'place')
        return

    def checkMediaCollection(self, results, query, match, options, order):
        types = self.__typesIntersection(query, match)
        if 'album' in types:
            self.checkWithComparator(AlbumEntityProxyComparator, results, query, match, options, order, 'album')
            return

        if 'tv' in types:
            self.checkWithComparator(TvEntityProxyComparator, results, query, match, options, order, 'tv')
            return

    def checkMediaItem(self, results, query, match, options, order):
        types = self.__typesIntersection(query, match)
        if 'track' in types:
            self.checkWithComparator(TrackEntityProxyComparator, results, query, match, options, order, 'track')
            return

        if 'movie' in types:
            self.checkWithComparator(MovieEntityProxyComparator, results, query, match, options, order, 'movie')
            return

        if 'book' in types:
            self.checkWithComparator(BookEntityProxyComparator, results, query, match, options, order, 'book')
            return

    def checkSoftware(self, results, query, match, options, order):
        types = self.__typesIntersection(query, match)

        if 'app' in types:
            self.checkWithComparator(AppEntityProxyComparator, results, query, match, options, order, 'app')
            return
    
    def resolve(self, query, source, **options):
        options = self.parseGeneralOptions(query, options)
        results = []
        index = 0
        
        for i in options['groups']:
            batch   = self.__resolveBatch(options['check'], query, source, (index, i) , options)
            index  += i
            results = self.__sortedPairs(results, batch)
            
            if self.__shouldFinish(query, results, options):
                break
        
        results = self.__finish(query, results, options)
        return results

    def parseGeneralOptions(self, query, options):
        """
        Most high level methods in this class accept an options dict as a means of customization.

        The following options are recognized:

        count -  a positive integer indicating the desired minimum result size (results may be smaller if the source is limited)
        max - a positive integer that sets the maximum number of results to return
        symmetric - a boolean which denotes if the comparison should by symmetric (i.e. a to b == b to a)
        negative - a boolean which denotes if negative weights should be used
        resolvedComparison -  a float which indicates a simple cutoff total comparison to consider something resolved
        pool - a positive integer indicating the size of the gevent pool to be used (use 1 for sequential)
        mins - an attribute-comparison dict which can be used to prune matches (useful for reducing execution time)
        """
        if 'callback' not in options:
            options['callback'] = lambda x,y: None
        if 'count' not in options:
            options['count'] = 1
        if 'limit' not in options:
            options['limit'] = 10
        if 'offset' not in options or options['offset'] is None:
            options['offset'] = 0
        if 'strict' not in options:
            options['strict'] = False
        if 'symmetric' not in options:
            options['symmetric'] = False
        if 'negative' not in options:
            options['negative'] = True
        if 'max' not in options:
            options['max'] = 1000000
        if 'resolvedComparison' not in options:
            options['resolvedComparison'] = .7
        if 'pool' not in options:
            options['pool'] = 10
        if 'mins' not in options:
            options['mins'] = {
                'types': 0.01
            }
        if 'groups' not in options:
            groups = [options['count'], 4, 10]
            options['groups'] = groups
        if 'check' not in options:
            if query.kind == 'person':
                options['check'] = self.checkPerson
            elif query.kind == 'place':
                options['check'] = self.checkPlace
            elif query.kind == 'media_collection':
                options['check'] = self.checkMediaCollection
            elif query.kind == 'media_item':
                options['check'] = self.checkMediaItem
            elif query.kind == 'software':
                options['check'] = self.checkSoftware
            else:
                #no generic test
                raise ValueError("no test for %s (%s)" % (query.name, query.kind))
        
        return options

    def __typesIntersection(self, q, m):
        try:
            return set(q.types).intersection(m.types)
        except:
            return set()

    def __sortedPairs(self, results, batch):
        results.extend(batch)
        def pairSort(pair):
            return -pair[0]['total']
        return sorted(results , key=pairSort)
    
    def __resolveBatch(self, check, query, source, section, options):
        start, count = section
        results = []
        entries = source(start, count)
        pool = Pool(options['pool'])
        for i in range(len(entries)):
            entry = entries[i]
            pool.spawn(check, results, query, entry, options, start+i)
        pool.join()
        
        return results

    def __shouldFinish(self, query, results, options):
        num_results = len(results)
        
        if num_results == 0:
            return False # TODO: is this right?
        elif num_results >= options['max']:
            return True
        elif num_results < options['count']:
            return False
        else:
            cutoff = options['resolvedComparison']
            if results[0][0]['total'] >= cutoff:
                return True
        return False

    def __finish(self, query, results, options):
        for result in results:
            result[0]['resolved'] = False
        if len(results) > 0 and results[0][0]['total'] > options['resolvedComparison']:
            results[0][0]['resolved'] = True
        return results

def demo(generic_source, default_title, subcategory=None):
    """
    Generic command-line demo function

    usage:
    python SOURCE_MODULE.py [ title [ subcategory [ count ] ] ]

    This demo queries the EntityDB for an entity matching the
    given title (or default_title). If a subcategory is given,
    the query is restricted to that category. Otherwise, the
    query is title-based and the type is determined by the 
    results subcategory.

    Once an entity is selected, it is converted to a query and
    resolved against the given source, with extremely verbose
    output enabled (not necessarily to logger, possibly stdout).
    The count option (1 by default) will be passed to resolve.

    If the entity was successfully resolved, demo() will attempt to
    invert it using a StampedSource. The result of this inversion 
    will also be verbosely outputted. 
    """
    import sys
    from resolve import StampedSource
    from api import Schemas

    title = default_title
    count = 1

    resolver = Resolver(verbose=True)
    entity_source = StampedSource.StampedSource()
    index = 0

    print(sys.argv)
    if len(sys.argv) > 1:
        title = sys.argv[1]
    if len(sys.argv) > 2:
        subcategory = sys.argv[2]
    if len(sys.argv) > 3:
        count = int(sys.argv[3])
    if len(sys.argv) > 4:
        index = int(sys.argv[3])

    from api.MongoStampedAPI import MongoStampedAPI
    api = MongoStampedAPI()
    db = api._entityDB
    query = {'titlel':title.lower()}
    if subcategory is not None:
        query['subcategory'] = subcategory
    else:
        query = { 'titlel' : title.lower() }
    pprint(query)
    cursor = db._collection.find(query)
    if cursor.count() <= index:
        print("Could not find a matching entity for %s" % title)
        return
    result = cursor[index]
    entity = db._convertFromMongo(result)
    proxy = entity_source.proxyFromEntity(entity)
    results = resolver.resolve(proxy, generic_source.matchSource(proxy), count=count)
    print '%s Results' % len(results)
    pprint(results)
    print("\n\nFinal result:\n")
    print(proxy)
    if len(results) > 0:
        best = results[0]
        pprint(best[0])
        pprint(best[1])
        if best[0]['resolved']:
            print("\nAttempting to invert")
            new_query = best[1]
            new_results = resolver.resolve(new_query, entity_source.matchSource(new_query), count=1)
            print('Inversion results:\n%s' % pformat(new_results) )
            if len(new_results) > 0 and new_results[0][0]['resolved']:
                best = new_results[0][1]
                if best.key == proxy.key:
                    print("Inversion succesful")
                else:
                    print("Inverted to different entity! (dup or false positive)")
            else:
                print("Inversion failed! (low asymetric comparison?)")

            # entityProxy = EntityProxyContainer(new_query)
            # blank = entityProxy.buildEntity()

            # pprint(blank)
            return results[0]
        print('\nFound results, but none are resolved')
    else:
        print("No results")
    return None
