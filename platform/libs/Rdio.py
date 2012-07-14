#!/usr/bin/env python

"""
Rdio wrapper

Notes:
to get tracks in playlists use: extras='trackKeys'

Sample user key (don't use much, it's mine -Landon)
('dnrkqfbtek39678h37y5u2ke38rzxvkeywfhgsbqn8s9z45rx9mjrmagcds6cf3w', 'fpdNE4EgBHgz')


DONE - gzip support (if available)
DONE - rate-limiting

TODO:
improve unicode support (i.e. The Do)
documentation
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'Rdio', 'globalRdio' ]

import Globals
from logs   import report
try:
    import urllib2, urllib
    from libs import TwitterOAuth as oauth
    import urllib
    import logs
    
    from libs.RateLimiter            import RateLimiter, RateException
    from libs.LRUCache               import lru_cache
    from libs.CachedFunction         import cachedFn
    from libs.CountedFunction   import countedFn
    from urlparse               import parse_qsl
    from urllib2                import HTTPError
    from urllib                 import quote_plus
    from django.utils.encoding  import iri_to_uri
    from libs.Request           import service_request
    
    try:
        import json
    except ImportError:
        import simplejson as json
except:
    report()
    raise


def urlencode_utf8(params):
    return urllib.urlencode(params)
    """
    return '&'.join(
        (quote_plus(k, safe='/') + '=' + iri_to_uri(v)
            for k, v in params.items()))
    """

class Rdio(object):

    def __init__(self, key='bzj2pmrs283kepwbgu58aw47', secret='xJSZwBZxFp', cps=5, cpd=15000):
        self.__key      = key
        self.__secret   = secret
        self.__consumer = oauth.Consumer(self.__key, self.__secret)
        self.__limiter  = RateLimiter(cps=cps, cpd=cpd)

    # note: these decorators add tiered caching to this function, such that 
    # results will be cached locally with a very small LRU cache of 64 items 
    # and also cached in Mongo or Memcached with the standard TTL of 7 days.
    @countedFn('Rdio (before caching)')
    @lru_cache(maxsize=64)
    @cachedFn()
    @countedFn('Rdio (after caching)')
    def method(self, method, **kwargs):
        # create the OAuth consumer credentials
        client = oauth.Client(self.__consumer)
        kwargs['method'] = method 
        
        for k,v in kwargs.items():
            if isinstance(v,int) or isinstance(v,float):
                kwargs[k] = str(v)
            elif isinstance(v,unicode):
                kwargs[k] = v.encode('utf-8')
        
        urlish = 'http://api.rdio.com/1/ POST %s' % urlencode_utf8(kwargs)

        response, content = service_request('rdio', 'POST', 'http://api.rdio.com/1/', header={'Accept-encoding':'gzip'},body=kwargs)

        return json.loads(content)

    def userMethod(self, token, token_secret, method, **kwargs): 
        kwargs['method'] = method 
        access_token = oauth.Token(token, token_secret)   
        client = oauth.Client(self.__consumer, access_token)
        
        with self.__limiter:
            logs.info('http://api.rdio.com/1/ POST %s' % urllib.urlencode(kwargs))
            response = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode(kwargs))
        
        return json.loads(response[1])

    def searchSuggestions(self, query, types="Artist,Album,Track", extras=None):
        """
        query:  required - the search prefix
        types:  optional - object types to include in results - a comma separated list of: "Artist", "Album", "Track", "Playlist" or "User"
        extras: optional - a list of additional fields to return - a list, comma separated
        """
        params = { 'query' : query, 'types': types }
        if extras is not None:
            params['extras'] = extras
        return self.method('searchSuggestions', **params)


__globalRdio = None

def globalRdio():
    global __globalRdio
    
    if __globalRdio is None:
        __globalRdio = Rdio()
    
    return __globalRdio

def demo(method, **params):
    import pprint
    rdio = globalRdio()
    pprint.pprint(rdio.method(method, **params))

if __name__ == '__main__':
    import sys
    
    method = 'search'
    params = {'query':'Katy Perry','types':'Artist'}
    
    if len(sys.argv) > 1:
        method = sys.argv[1]
    
    if len(sys.argv) > 2:
        params = {}
        for arg in sys.argv[2:]:
            pair = arg.split('=')
            params[pair[0]] = pair[1]
    
    demo(method, **params)

