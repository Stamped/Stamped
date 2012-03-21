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
    from GenericSource              import GenericSource
    from utils                      import lazyProperty
    import logs
    from Resolver                   import *
    from pprint                     import pformat
    from libs.LibUtils              import parseDateString
    from Schemas                    import Entity
    from datetime                   import datetime
    from bson                       import ObjectId
    from iTunesSource               import iTunesSource
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
    def searchSources(self):
        return [iTunesSource()]

    @lazyProperty
    def __resolver(self):
        return Resolver()

    def search(self, query_string, count=10, coordinates=None):
        query = QuerySearchAll(query_string, coordinates)
        results = []
        for source in self.searchSources:
            source_results = source.resolve(query, count=count)
            results.extend([ x[1] for x in source_results])
        def gen(start, count):
            return results[start:count]
        final_results = self.__resolver.resolve(query, gen, count=count)
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
    pprint.pprint(results)