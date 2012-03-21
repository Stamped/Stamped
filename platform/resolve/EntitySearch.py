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
    import logs
    from Resolver                   import *
    from pprint                     import pformat
    from libs.LibUtils              import parseDateString
    from Schemas                    import Entity
    from datetime                   import datetime
    from bson                       import ObjectId
    from iTunesSource               import iTunesSource
    from RdioSource                 import RdioSource
except:
    report()
    raise

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

    def search(self, query_string, count=10, coordinates=None):
        query = QuerySearchAll(query_string, coordinates)
        results = []
        sources = {
            'itunes':iTunesSource().matchSource(query),
            'rdio':RdioSource().matchSource(query),
        }
        def gen():
            try:
                all_results = {}
                for name,source in sources.items():
                    source_results = self.__resolver.resolve(query, source, count=count)
                    all_results[name] = source_results
                while True:
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
                                print("skipped %s with value %s" % (name, cur_best[0]['total']))
                    if best is not None:
                        del all_results[best_name][0]
                        print("Chose %s with value %s" % (best_name, best[0]['total']))
                        yield best[1]
                    else:
                        break
            except GeneratorExit:
                pass
        
        final_results = self.__resolver.resolve(query, generatorSource(gen()), count=count)
        return final_results
  
if __name__ == '__main__':
    import sys
    import pprint
    count = 10
    query = "Katy Perry Firework"
    if len(sys.argv) > 1:
        query = sys.argv[1]
    if len(sys.argv) > 2:
        count = int(sys.argv[2])
    results = EntitySearch().search(query, count=count)
    print("Final Search Results")
    n = len(results)
    # for result in results:
    for i in range(len(results)):
        result = results[n - 1]
        print '\n%3s %s' % (n, '=' * 37)
        scores = result[0]
        weights = scores['weights']
        total_weight = 0.0
        for k, v in weights.iteritems():
            total_weight = total_weight + float(v)
        print '%16s   Val     Wght     Total' % ' '
        for k, v in weights.iteritems():
            s = float(scores[k])
            w = float(weights[k])
            t = 0
            if total_weight > 0:
                t = s * w / total_weight
            print '%16s  %.2f  *  %.2f  =>  %.2f' % (k, s, w, t)
        print ' ' * 36, '%.2f' % scores['total']
        pprint.pprint(result[1])
        n = n - 1

