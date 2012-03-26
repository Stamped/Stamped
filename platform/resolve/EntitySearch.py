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
    from GenericSource              import generatorSource
    from utils                      import lazyProperty
    from gevent.pool                import Pool
    import logs
    from Resolver                   import *
    from pprint                     import pformat
    from libs.LibUtils              import parseDateString
    from Schemas                    import Entity
    from datetime                   import datetime
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

    def __init__(self, query_string, coordinates=None):
        ResolverSearchAll.__init__(self)
        self.__query_string = query_string
        self.__coordinates = coordinates

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
    def key(self):
        return ''

    @property
    def name(self):
        return ''

    @property
    def source(self):
        return 'search'

class EntitySearch(object):

    @lazyProperty
    def __resolver(self):
        return Resolver()

    def __helper(self, query, count, name, source_f, results_list):
        source = source_f()
        def callback(result, order):
            if _verbose:
                print("%3d from %s" % (order, name))
            results_list.append((name,result))
        self.__resolver.resolve(query, source, count=count, callback=callback, groups=[1,2,7])

    def search(self, query_string, count=10, coordinates=None, types=None):
        timeout = 6
        before  = time()
        query   = QuerySearchAll(query_string, coordinates)
        results = []
        sources = {
            'itunes':   lambda: iTunesSource().searchAllSource(query, timeout=timeout, types=types),
            'rdio':     lambda: RdioSource().searchAllSource(query, timeout=timeout, types=types),
            'stamped':  lambda: StampedSource().searchAllSource(query, timeout=timeout, types=types),
            'factual':  lambda: FactualSource().searchAllSource(query, timeout=timeout, types=types),
            'tmdb':     lambda: TMDBSource().searchAllSource(query, timeout=timeout, types=types),
            'spotify':  lambda: SpotifySource().searchAllSource(query,timeout=timeout, types=types),
            'amazon':  lambda: AmazonSource().searchAllSource(query,timeout=timeout, types=types),
            'googleplaces':  lambda: GooglePlacesSource().searchAllSource(query, timeout=timeout, types=types),
        }

        results_list = []
        pool = Pool(len(sources))

        for name, source_f in sources.items():
            pool.spawn(self.__helper, query, count, name, source_f, results_list)

        pool.join(timeout=timeout)

        all_results = {}
        total = 0
        for name,result in list(results_list):
            source_results = all_results.setdefault(name,[])
            source_results.append(result)
            total += 1

        for name,source_results in all_results.items():
            all_results[name] = sortedResults(source_results)

        if _verbose:
            print("\n\n\nGenerated %s results in %f seconds from: %s\n\n\n" % (
                total, time() - before, ' '.join([ '%s:%s' % (k, len(v)) for k,v in all_results.items()])
            ))
        
        before2 = time()
        chosen  = []
        
        while len(chosen) < count:
            best = None
            best_name = None
            for name,results in list(all_results.items()):
                if len(results) == 0:
                    del all_results[name]
                else:
                    cur_best = results[0]
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
            print("\n\n\nDedupped %s results in %s seconds\n\n\n" % (total - len(chosen), time() - before2))
        return chosen

    def searchEntities(self, query_string, count=10, coords=None, category=None, subcategory=None):
        types = None
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

        coordinates = None
        if coords is not None:
            coordinates = (coords.lat, coords.lng)

        sources = {
            'itunes':       iTunesSource(),
            'rdio':         RdioSource(),
            'stamped':      StampedSource(),
            'factual':      FactualSource(),
            'tmdb':         TMDBSource(),
            'spotify':      SpotifySource(),
            'googleplaces': GooglePlacesSource(),
            'amazon':       AmazonSource(),
        }
        
        search = self.search(query_string, count=count, coordinates=coordinates, types=types)

        results = []

        for item in search:
            entity = Entity()
            source = item[1].target.source
            if source not in sources:
                source = sources['stamped']
            sources[source].enrichEntityWithWrapper(item[1].target, entity)
            results.append(entity)
        
        return results

def demo():
    import sys
    import pprint
    count = 10
    query = "Katy Perry Firework"
    coordinates = None
    if len(sys.argv) > 1:
        query = sys.argv[1]
    if len(sys.argv) > 2:
        count = int(sys.argv[2])
    if len(sys.argv) > 3:
        coordinates = tuple([ float(v) for v in sys.argv[3].split(',') ])
    results = EntitySearch().search(query, count=count, coordinates=coordinates)

    print("Final Search Results")
    print(formatResults(results))

    # for result in results:
    #     entity = Entity()
    #     sources = {
    #         'itunes':   iTunesSource(),
    #         'rdio':     RdioSource(),
    #         'stamped':  StampedSource(),
    #         'factual':  FactualSource(),
    #         'tmdb':     TMDBSource(),
    #         'spotify':  SpotifySource(),
    #         'googleplaces':  GooglePlacesSource(),
    #         'amazon':  AmazonSource(),
    #     }
    #     s = result[1].target.source
    #     if s in sources:
    #         sources[s].enrichEntityWithWrapper(result[1].target, entity)
    #     else:
    #         StampedSource().enrichEntityWithWrapper(result[1].target, entity)
    #     print(pformat(entity.value))

if __name__ == '__main__':
    _verbose = True
    demo()

