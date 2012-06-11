#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs import report

try:
    import keys.aws
    import bottlenose   
    import logs
    
    from LibUtils       import xmlToPython
    from LRUCache       import lru_cache
    from CachedFunction import cachedFn
except:
    report()
    raise

__all__      = [ "Amazon" ]
ASSOCIATE_ID = 'stamped01-20'

class Amazon(object):
    """
        Amazon API wrapper (2)
    """
    
    def __init__(self):
        self.amazon = bottlenose.Amazon(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY, ASSOCIATE_ID)

    # note: these decorators add tiered caching to this function, such that 
    # results will be cached locally with a very small LRU cache of 64 items 
    # and also cached in Mongo or Memcached with the standard TTL of 7 days.
    @lru_cache(maxsize=64)
    @cachedFn()
    def item_search(self, **kwargs):
        logs.info("Amazon API: ItemSearch %s" % kwargs)
        return self._item_helper(self.amazon.ItemSearch, **kwargs)

    # note: these decorators add tiered caching to this function, such that 
    # results will be cached locally with a very small LRU cache of 64 items 
    # and also cached in Mongo or Memcached with the standard TTL of 7 days.
    @lru_cache(maxsize=64)
    @cachedFn()
    def item_lookup(self, **kwargs):
        logs.info("Amazon API: ItemLookup %s" % kwargs)
        return self._item_helper(self.amazon.ItemLookup, **kwargs)
    
    def _item_helper(self, func, **kwargs):
        string = func(**kwargs)
        
        """# useful for debugging amazon queries
        if 'ItemId' in kwargs:
            f = open('amazon.%s.xml' % kwargs['ItemId'], 'w')
            f.write(string)
            f.close()
        """
        
        return xmlToPython(string)

__globalAmazon = None

def globalAmazon():
    global __globalAmazon
    if __globalAmazon is None:
        __globalAmazon = Amazon()
    
    return __globalAmazon

def main():
    api = Amazon()
    import sys
    import re
    import pprint

    method = 'search'
    
    args = {
    }
    if len(sys.argv) > 1:
        method = sys.argv[1]
        for pair in sys.argv[2:]:
            l = pair.split('=')
            args[l[0]] = l[1]
    
    if method == 'search' or method == "ItemSearch":
        pprint.pprint(api.item_search(**args))
    elif method == 'lookup' or method == 'ItemLookup':
        pprint.pprint(api.item_lookup(**args))
    else:
        print('Unknown method %s' % method)

if __name__ == '__main__':
    main()

