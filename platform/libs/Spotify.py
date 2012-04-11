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
    import logs, urllib
    from RateLimiter            import RateLimiter, RateException
    from urllib2                import HTTPError
    from errors                 import StampedHTTPError
    from LRUCache               import lru_cache
    from Memcache               import memcached_function
    
    try:
        import json
    except ImportError:
        import simplejson as json
except:
    report()
    raise

class Spotify(object):

    def __init__(self):
        self.__limiter = RateLimiter(cps=10)
    
    # note: these decorators add tiered caching to this function, such that 
    # results will be cached locally with a very small LRU cache of 64 items 
    # and also cached remotely via memcached with a TTL of 7 days
    @lru_cache(maxsize=64)
    @memcached_function(time=7*24*60*60)
    def method(self, service, method, **params):
        with self.__limiter:
            try:
                base_url = 'http://ws.spotify.com/%s/1/%s.json' % (service, method)
                for k,v in params.items():
                    if isinstance(v,int) or isinstance(v,float):
                        params[k] = str(v)
                    elif isinstance(v,unicode):
                        params[k] = v.encode('utf-8')
                url = '%s?%s' % (base_url, urllib.urlencode(params))
                logs.info( url )
                result = urllib.urlopen(url).read()
            except HTTPError as e:
                raise StampedHTTPError('spotify threw an %s exception' % e.code,e.code,e.message)
        
        return json.loads(result)
    
    def search(self, method, **params):
        return self.method('search', method, **params)
    
    def lookup(self, uri, extras=None):
        if extras is None:
            return self.method('lookup', '', uri=uri)
        else:
            return self.method('lookup', '', uri=uri, extras=extras)

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
    method = 'artist'
    params = {'q':'Katy Perry'}
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


