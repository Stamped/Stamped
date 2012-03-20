#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'EntitySearch' ]

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
except:
    report()
    raise


class EntitySearch(object):

    def createSearchQuery(self, query_string, category=None, coordinates=None):
        return None

    @lazyProperty
    def searchSources(self):
        return []

    @lazyProperty
    def __resolver(self):
        return Resolver()

    def search(self, query_string, count=10, **kwargs):
        query = createSearchQuery(query_string, **kwargs)
        results = []
        for source in self.searchSources:
            source_results = source.resolve(query, count=count)
            results.extend(source_results)
        def gen(start, count):
            return results[start:count]
        final_results = self.__resolver.resolve(query, gen, count=count)
        return final_results
  
if __name__ == '__main__':
    import sys
    import pprint
    resutls = EntitySearch().search(sys.argv[1])
    pprint.pprint(results)