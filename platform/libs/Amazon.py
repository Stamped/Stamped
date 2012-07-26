#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs import report

try:
    from libs import bottlenose
    import logs

    from libs.LibUtils        import xmlToPython
    from libs.LRUCache        import lru_cache
    from libs.CachedFunction  import cachedFn
    from libs.CountedFunction import countedFn
    from APIKeys              import get_api_key
except:
    report()
    raise

__all__         = [ "Amazon" ]
ASSOCIATE_ID        = get_api_key('amazon', 'associate_id')
AWS_ACCESS_KEY_ID   = get_api_key('amazon', 'aws_access_key_id')
AWS_SECRET_KEY      = get_api_key('amazon', 'aws_secret_key')

class Amazon(object):
    """
        Amazon API wrapper (2)
    """

    def __init__(self):
        self.amazon = bottlenose.Amazon(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY, ASSOCIATE_ID)

    # note: these decorators add tiered caching to this function, such that
    # results will be cached locally with a very small LRU cache of 64 items
    # and also cached in Mongo or Memcached with the standard TTL of 7 days.
    @countedFn(name='Amazon (before caching)')
    @lru_cache(maxsize=64)
    @cachedFn()
    @countedFn(name='Amazon (after caching)')
    def item_search(self, timeout=None, **kwargs):
        logs.info("Amazon API: ItemSearch %s" % kwargs)
        return self._item_helper(self.amazon.ItemSearch, timeout, **kwargs)

    # note: these decorators add tiered caching to this function, such that
    # results will be cached locally with a very small LRU cache of 64 items
    # and also cached in Mongo or Memcached with the standard TTL of 7 days.
    @countedFn(name='Amazon (before caching)')
    @lru_cache(maxsize=64)
    @cachedFn()
    @countedFn(name='Amazon (after caching)')
    def item_lookup(self, timeout=None, **kwargs):
        logs.info("Amazon API: ItemLookup %s" % kwargs)
        return self._item_helper(self.amazon.ItemLookup,
                                 timeout,
                                 **kwargs)

    def _item_helper(self, func, timeout=None, **kwargs):
        return xmlToPython(func(timeout, **kwargs))

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

