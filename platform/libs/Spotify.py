#!/usr/bin/env python

"""
    Interface for Spotify Metadata API
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = ['Spotify', 'globalSpotify']

import Globals
from logs import report

try:
    import logs, httplib, urllib
    from libs.RateLimiter import RateLimiter, RateException
    from libs.LRUCache import lru_cache
    from libs.CachedFunction import cachedFn
    from libs.CountedFunction import countedFn
    from errors import StampedThirdPartyError
    from libs.Request import service_request
    
    try:
        import json
    except ImportError:
        import simplejson as json
except:
    report()
    raise

class Spotify(object):

    def __init__(self):
        self.__limiter = RateLimiter(cps=4)

    # note: these decorators add tiered caching to this function, such that 
    # results will be cached locally with a very small LRU cache of 64 items 
    # and also cached in Mongo or Memcached with the standard TTL of 7 days.
    @countedFn('Spotify (before caching)')
    @lru_cache(maxsize=64)
    @cachedFn()
    @countedFn('Spotify (after caching)')
    def method(self, service, method, priority='low', **params):
        base_url = 'http://ws.spotify.com/%s/1/%s.json' % (service, method)
        for k,v in params.items():
            if isinstance(v,int) or isinstance(v,float):
                params[k] = str(v)
            elif isinstance(v,unicode):
                params[k] = v.encode('utf-8')
        response, content = service_request('spotify', 'GET', base_url, query_params=params, priority=priority)
        if response.status >= 200 and response.status < 300:
            return json.loads(content)
        raise StampedThirdPartyError('Spotify returned error code: ' + str(response.status))
        
    
    def search(self, method, priority='low', **params):
        return self.method('search', method, priority, **params)
    
    def lookup(self, uri, extras=None, priority='low'):
        if extras is None:
            return self.method('lookup', '', priority, uri=uri)
        else:
            return self.method('lookup', '', priority, uri=uri, extras=extras)

__globalSpotify = None

def globalSpotify():
    global __globalSpotify
    if __globalSpotify is None:
        __globalSpotify = Spotify()
    
    return __globalSpotify

def demo(service, method, **params):
    import pprint
    spotify = Spotify()
    pprint.pprint(spotify.method(service, method, **params))

if __name__ == '__main__':
    import sys
    
    service = 'search'
    method  = 'artist'
    params  = { 'q' : 'Katy Perry' }
    
    if len(sys.argv) > 1:
        service = sys.argv[1]
    
    if len(sys.argv) > 2:
        method = sys.argv[2]
    
    if len(sys.argv) > 3:
        params = {}
        for arg in sys.argv[3:]:
            pair = arg.split('=')
            params[pair[0]] = pair[1]
    
    demo(service, method, **params)

