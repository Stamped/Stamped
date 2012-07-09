#!/usr/bin/env python

"""
Barebones Apple iTunes Wrapper
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = ['iTunes', 'globaliTunes']

import Globals
from logs import report

try:
    import logs, urllib
    
    from utils                  import getFile
    from urllib2                import HTTPError
    from libs.RateLimiter            import RateLimiter, RateException
    from libs.LRUCache               import lru_cache
    from libs.CachedFunction         import cachedFn
    from libs.CountedFunction   import countedFn
    
    try:
        import json
    except ImportError:
        import simplejson as json
except:
    report()
    raise

class iTunes(object):

    def __init__(self):
        self.setMaxQps(10)
        pass

    def setMaxQps(self, max_qps):
        self.__limiter = RateLimiter(cps=max_qps)
    
    # note: these decorators add tiered caching to this function, such that 
    # results will be cached locally with a very small LRU cache of 64 items 
    # and also cached in Mongo or Memcached with the standard TTL of 7 days.
    @countedFn('iTunes (before caching)')
    @lru_cache(maxsize=64)
    @cachedFn()
    @countedFn('iTunes (after caching)')
    def method(self, method, **params):
        try:
            url = 'http://itunes.apple.com/%s' % method
            with self.__limiter:
                try:
                    logs.info("%s?%s" % (url, urllib.urlencode(params)))
                except Exception:
                    report()

                result = getFile(url, params=params)
        except HTTPError as e:
            logs.warning("iTunes threw an exception (%s): %s" % (e.code, e.message))
            raise Exception
        
        result = json.loads(result)

        if result is None:
            raise Exception('iTunes returned "None" result')

        return result

__globaliTunes = None

def globaliTunes():
    global __globaliTunes
    
    if __globaliTunes is None:
        __globaliTunes = iTunes()

    return __globaliTunes

def demo(method, **params):
    import pprint
    itunes = iTunes()
    pprint.pprint(itunes.method(method, **params))

if __name__ == '__main__':
    import sys
    method = 'search'
    params = {'term':'Katy Perry'}
    if len(sys.argv) > 1:
        method = sys.argv[1]
    if len(sys.argv) > 2:
        params = {}
        for arg in sys.argv[2:]:
            pair = arg.split('=')
            params[pair[0]] = pair[1]
    demo(method, **params)


