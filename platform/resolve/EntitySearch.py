#!/usr/bin/env python

"""
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
    from Schemas                    import Entity
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
    from Entity                     import subcategories
except:
    report()
    raise

_verbose = False

class QuerySearchAll(ResolverSearchAll):
    
    def __init__(self, query_string, coords=None, types=None, local=False):
        ResolverSearchAll.__init__(self)
        
        if not local:
            if types and 'place' not in types:
                # if we're filtering by category / subcategory and the filtered results 
                # couldn't possibly contain a location, then ensure that coords are 
                # disabled
                coords = None
            else:
                # process 'in' or 'near' location hint
                result = libs.worldcities.try_get_region(query_string)
                
                if result is not None:
                    query_string, coords, region_name = result
                    if types is None: types = set()
                    types.add('place')
                    
                    logs.info("[search] using region %s at %s (parsed from '%s')" % 
                              (region_name, coords, query_string))
        
        if local:
            if types is None: types = set()
            types.add('place')
        
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
            if query.types is None or result[1].subtype in query.types:
                source_results = all_results.setdefault(name,[])
                source_results.append(result)
                total += 1
        
        for name, source_results in all_results.items():
            all_results[name] = sortedResults(source_results)
        
        if _verbose:
            print("\n\n\nGenerated %d results in %f seconds from: %s\n\n\n" % (
                total, time() - before, ' '.join([ '%s:%s' % (k, len(v)) for k,v in all_results.items()])
            ))
        
        before2 = time()
        chosen  = []
        limit   = max(0, min(total, limit if limit else total))
        
        while len(chosen) < limit:
            best_name = None
            best = None
            
            for name, source_results in list(all_results.items()):
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
                
                if len(dups) == 0 or not dups[0][0]['resolved']:
                    chosen.append(best)
                else:
                    if _verbose:
                        print("Discarded %s:%s as a duplicate to %s:%s" % (cur.source, cur.name, dups[0][1].source, dups[0][1].name))
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
            if subcategory == 'song':
                subcategory = 'track'
            types = set(subcategory)
        elif category is not None:
            types = set()
            for s, c in subcategories.iteritems():
                if category == c:
                    if s == 'song':
                        s = 'track'
                    types.add(s)
        
        search  = self.search(query, 
                              coords    = coords, 
                              full      = full, 
                              local     = local, 
                              offset    = offset, 
                              limit     = limit, 
                              types     = types)
        
        for item in search:
            entity = Entity()
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
    
    return (options, args)

def demo():
    options, args = parseCommandLine()
    searcher = EntitySearch()
    
    results = searcher.search(query     = args[0], 
                              coords    = options.location, 
                              full      = not options.quick, 
                              local     = options.Local, 
                              offset    = options.offset, 
                              limit     = options.limit)
    
    print("Final Search Results")
    print(formatResults(results, verbose=options.verbose))

if __name__ == '__main__':
    _verbose = True
    demo()

