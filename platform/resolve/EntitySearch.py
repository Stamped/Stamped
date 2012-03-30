#!/usr/bin/env python

"""
    Entrypoint for resolver-based entity search across all available sources.
"""

"""
TODO:
    * fix TMDB search only returning one result in many cases
    * add caching to third-party API calls (RateLimiter)
    * add regression-oriented tests to search
        * run these tests regularly on prod via cron job
        * verify:
            * movies
                * movie in theaters (pull from fandango)
                * popular movie
                * really old movie
                * different language movie
            * tv
                * new / recent shows
                * upcoming shows
                * really popular shows
                * really old shows
                * different language show
            * tracks
                * itunes top chart lists
                * rdio / spotify top chart lists
                * track_name by artist_name
                * track_name artist_name
                * track_name album_name artist_name (and all permutations)
                * different language track
            * albums
                * itunes otp chart lists
                * album_name
                * album_name by artist_name
                * album_name artist_name (and vice-versa)
            * artist
                * search for artist alias / non-exact name
                    * (e.g., jayz, jay-z, and jay z should all work as expected)
                * search for track => artist in results
                * search for album => artist in results
                * international artist
            * app
                * app_name by company_name
                * app_name company_name (and vice-versa)
                * search for ipad-only app
            * restaurant
                * same permutations as place
                * new / recent restaurants from opentable
                * remote restaurants
                * search for generic chain (e.g., mcdonald's)
                * search for really unique name (e.g., absinthe)
            * place
                * search w/ and w/out coordinates
                * search w/ and w/out location hints
                * several international places
            * book
                * new / recent book
                * book_name
                * book_name by artist_name
                * book_name artist_name (and vice-versa)
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'EntitySearch', 'QuerySearchAll' ]

import Globals
from logs import report

try:
    import logs, sys, utils
    import libs.worldcities
    
    from Resolver                   import *
    from GenericSource              import generatorSource
    from utils                      import lazyProperty
    from gevent.pool                import Pool
    from pprint                     import pprint
    from libs.LibUtils              import parseDateString
    from Schemas                    import BasicEntity
    from datetime                   import datetime
    from optparse                   import OptionParser
    from bson                       import ObjectId
    from iTunesSource               import iTunesSource
    from RdioSource                 import RdioSource
    from StampedSource              import StampedSource
    from FactualSource              import FactualSource
    from TMDBSource                 import TMDBSource
    from SpotifySource              import SpotifySource
    from GooglePlacesSource         import GooglePlacesSource
    from AmazonSource               import AmazonSource
    from time                       import time
    from Entity                     import subcategories, deriveTypesFromSubcategories
except:
    report()
    raise

_verbose = False

class QuerySearchAll(ResolverSearchAll):
    
    def __init__(self, query_string, coords=None, types=None, local=False):
        ResolverSearchAll.__init__(self)
        
        if local:
            if types is None: types = set()
            types.add('place')
        else:
            if types and 'place' not in types:
                # if we're filtering by category / subcategory and the filtered results 
                # couldn't possibly contain a location, then ensure that coords are 
                # disabled
                coords = None
            else:
                # process 'in' or 'near' location hint
                result = libs.worldcities.try_get_region(query_string)
                
                if result is not None:
                    new_query_string, coords, region_name = result
                    if types is None: types = set()
                    types.add('place')
                    
                    logs.info("[search] using region %s at %s (parsed from '%s')" % 
                              (region_name, coords, query_string))
                    query_string = new_query_string
        
        self.__query_string = query_string
        self.__coordinates  = coords
        self.__types        = types
        self.__local        = local
    
    @property
    def query_string(self):
        return self.__query_string
    
    @property
    def coordinates(self):
        return self.__coordinates
    
    @property
    def keywords(self):
        return self.query_string.split()
    
    @property
    def types(self):
        return self.__types
    
    @property
    def local(self):
        return self.__local
    
    @property
    def key(self):
        return ''
    
    @property
    def name(self):
        return ''
    
    @property
    def types(self):
        return self.__types
    
    @property
    def source(self):
        return 'search'

class EntitySearch(object):

    def __init__(self):
        self._sources = [
            StampedSource(), 
            iTunesSource(), 
            TMDBSource(), 
            GooglePlacesSource(), 
            FactualSource(), 
            AmazonSource(), 
            RdioSource(), 
            SpotifySource(), 
        ]
        
        self._sources_map = { }
        for source in self._sources:
            self._sources_map[source.sourceName] = source
    
    @lazyProperty
    def __resolver(self):
        return Resolver()

    def __search_helper(self, query, limit, offset, source, results, **kwargs):
        name = source.sourceName
        gen  = source.searchAllSource(query, **kwargs)
        
        def callback(result, order):
            if _verbose:
                print("%3d from %s" % (order, name))
            results.append((name,result))
        
        self.__resolver.resolve(query, gen, count=limit, callback=callback, groups=[1,2,7])
    
    def search(self, 
               query, 
               coords   = None, 
               full     = True, 
               local    = False, 
               types    = None, 
               offset   = 0, 
               limit    = 10):
        
        before  = time()
        query   = QuerySearchAll(query, coords, types, local)
        pool    = Pool(len(self._sources))
        results = []
        timeout = 6
        
        # NOTE: order is important here; e.g., we want to give precedence to 
        # certain third-party APIs to begin their requests before others.
        for source in self._sources:
            if not full and source.sourceName != 'stamped':
                # ignore any external sources if full search is disabled
                continue
            
            pool.spawn(self.__search_helper, query, limit, offset, source, results, timeout=timeout)
        
        pool.join(timeout=timeout)
        
        all_results = {}
        total = 0
        
        for name, result in results:
            # TODO: Check song (subcategory) vs track (query.types)
            if query.types is None or result[1].subtype in query.types:
                source_results = all_results.setdefault(name,[])
                source_results.append(result)
                total += 1
            else:
                logs.info("Filtered out %s (subcategory=%s, type=%s)" % 
                          (result[1].name, result[1].subcategory, result[1].subtype))
        
        logs.info("")
        
        for name, source_results in all_results.iteritems():
            all_results[name] = sortedResults(source_results)
        
        if _verbose:
            print("\n\n\nGenerated %d results in %f seconds from: %s\n\n\n" % (
                total, time() - before, ' '.join([ '%s:%s' % (k, len(v)) for k,v in all_results.iteritems()])
            ))
        
        before2 = time()
        chosen  = []
        limit   = max(0, min(total, limit if limit else total))
        
        while len(chosen) < limit:
            best_name = None
            best = None
            
            for name, source_results in list(all_results.iteritems()):
                if len(source_results) == 0:
                    del all_results[name]
                else:
                    cur_best = source_results[0]
                    if best is None or cur_best[0]['total'] > best[0]['total']:
                        best = cur_best
                        best_name = name
                    else:
                        if _verbose:
                            print("skipped %s with value %s" % (name, cur_best[0]['total']))
            
            if best is not None:
                del all_results[best_name][0]
                
                if _verbose:
                    print("Chose %s with value %s" % (best_name, best[0]['total']))
                cur = best[1]
                
                def dedup():
                    for entry in chosen:
                        target = entry[1].target
                        if target.type == cur.target.type:
                            yield target
                
                dups = self.__resolver.resolve(cur.target, generatorSource(dedup()), count=1)
                
                if len(dups) > 0 and dups[0][0]['resolved']:
                    if _verbose:
                        print("Discarded %s:%s as a duplicate to %s:%s" % (cur.source, cur.name, dups[0][1].source, dups[0][1].name))
                        
                        print(formatResults(dups[0:1], verbose=True))
                else:
                    chosen.append(best)
            else:
                break
        
        if _verbose:
            print("\n\n\nDedupped %d results in %f seconds\n\n\n" % (total - len(chosen), time() - before2))
        
        return chosen
    
    def searchEntities(self, 
                       query, 
                       coords       = None, 
                       full         = True, 
                       local        = False, 
                       category     = None, 
                       subcategory  = None, 
                       offset       = 0, 
                       limit        = 10):
        results = []
        types   = None
        
        if subcategory is not None:
            types = set(deriveTypesFromSubcategories([subcategory]))
        elif category is not None:
            types = set()
            for s, c in subcategories.iteritems():
                if category == c:
                    t = set(deriveTypesFromSubcategories([s]))
                    for i in t:
                        types.add(deriveTypesFromSubcategories(i))

        try:
            if coords.lat is not None and coords.lng is not None:
                coords = (coords.lat, coords.lng)
            else:
                coords = None
        except:
            coords = None
        
        search  = self.search(query, 
                              coords    = coords, 
                              full      = full, 
                              local     = local, 
                              offset    = offset, 
                              limit     = limit, 
                              types     = types)
        
        for item in search:
            entity = BasicEntity()
            source = item[1].target.source
            
            if source not in self._sources_map:
                source = 'stamped'

            self._sources_map[source].enrichEntityWithWrapper(item[1].target, entity)
            results.append(entity)
        
        return results

def parseCommandLine():
    usage   = "Usage: %prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", action="store", 
        help="db to connect to (e.g., peach.db0; defaults to localhost)")
    
    parser.add_option("-l", "--limit", default=None, type="int", 
        help="limits the number of results to return")
    
    parser.add_option("-o", "--offset", default=0, type="int", 
        help="optional offset into results to support paging")
    
    parser.add_option("-L", "--Local", default=False, action="store_true", 
        help="enable local nearby search")
    
    parser.add_option("-a", "--a", default=None, type="string", 
        action="store", dest="location", help="location (lat/lng, e.g. '40.736,-73.989')")
    
    parser.add_option("-q", "--quick", default=False, action="store_true", 
        help="disable third party API queries")
    
    parser.add_option("-v", "--verbose", default=None, action="store_true", 
        help="turn verbosity on")
    
    parser.add_option("-c", "--category", default=None, type="string", 
        action="store", dest="category", 
        help="filters results by a given category")
    
    parser.add_option("-s", "--subcategory", default=None, type="string", 
        action="store", dest="subcategory", 
        help="filters results by a given subcategory")
    
    (options, args) = parser.parse_args()
    
    if len(args) <= 0:
        parser.print_help()
        sys.exit(1)
    
    if options.db:
        utils.init_db_config(options.db)
    
    if options.location:
        try:
            lat, lng = options.location.split(',')
            options.location = (float(lat), float(lng))
        except Exception:
            print "invalid location given '%s'" % options.location
            parser.print_help()
            sys.exit(1)
    
    if options.verbose is not None:
        global _verbose
        _verbose = options.verbose


    types   = None
    if options.subcategory is not None:
        if options.subcategory == 'song':
            options.subcategory = 'track'
        types = set(options.subcategory)
    elif options.category is not None:
        types = set()
        for s, c in subcategories.iteritems():
            if options.category == c:
                if s == 'song':
                    s = 'track'
                types.add(s)

    options.types = types
    
    return (options, args)

def demo():
    options, args = parseCommandLine()
    searcher = EntitySearch()
    
    results = searcher.search(query     = args[0], 
                              coords    = options.location, 
                              full      = not options.quick, 
                              local     = options.Local, 
                              offset    = options.offset, 
                              types     = options.types,
                              limit     = options.limit)
    
    print("Final Search Results")
    print(formatResults(results, verbose=options.verbose))

if __name__ == '__main__':
    _verbose = True
    demo()

