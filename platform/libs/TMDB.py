#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


__all__ = ['TMDB', 'globalTMDB']

import Globals
from logs   import report
try:
    import sys
    import json
    import urllib2
    import logs
    
    from urllib2         import HTTPError
    from gevent          import sleep
    from pprint          import pprint
    from RateLimiter     import RateLimiter, RateException
    from LRUCache        import lru_cache
    from CachedFunction  import cachedFn
    from CountedFunction import countedFn
except:
    report()
    raise

class TMDB(object):
    
    def __init__(self):
        self.__key = 'b4aaa79e39e12f8d066903b8574ee538'
        self.__limiter = RateLimiter(cps=5)
    
    def configuration(self):
        return self.__tmdb('configuration')
    
    def person_search(self, query, page=1):
        return self.__tmdb('search/person',query=query,page=page)
    
    def person_info(self, tmdb_id):
        return self.__tmdb('person/%s' %(tmdb_id,))
    
    def person_credits(self, tmdb_id):
        return self.__tmdb('person/%s/credits' %(tmdb_id,))
    
    def person_images(self, tmdb_id):
        return self.__tmdb('person/%s/images' %(tmdb_id,))
    
    def movie_latest(self, query, page=1):
        return self.__tmdb('latest/movie',query=query,page=page)
    
    def movie_search(self, query, page=1):
        return self.__tmdb('search/movie',query=query,page=page)
    
    def movie_info(self, tmdb_id):
        return self.__tmdb('movie/%s' %(tmdb_id,))
    
    def movie_casts(self, tmdb_id):
        return self.__tmdb('movie/%s/casts' %(tmdb_id,))
    
    def movie_keywords(self, tmdb_id):
        return self.__tmdb('movie/%s/keywords' %(tmdb_id,))
    
    def movie_alternative_titles(self, tmdb_id):
        return self.__tmdb('movie/%s/alternative_titles' %(tmdb_id,))
    
    def movie_images(self, tmdb_id):
        return self.__tmdb('movie/%s/images' %(tmdb_id,))
    
    def movie_releases(self, tmdb_id):
        return self.__tmdb('movie/%s/releases' %(tmdb_id,))
    
    def movie_trailers(self, tmdb_id):
        return self.__tmdb('movie/%s/trailers' %(tmdb_id,))
    
    def movie_translations(self, tmdb_id):
        return self.__tmdb('movie/%s/translations' %(tmdb_id,))
    
    def collection_info(self, tmdb_id):
        return self.__tmdb('collection/%s' %(tmdb_id,))

    # note: these decorators add tiered caching to this function, such that 
    # results will be cached locally with a very small LRU cache of 64 items 
    # and also cached in Mongo or Memcached with the standard TTL of 7 days.
    @countedFn(name='TMDB (before caching)')
    @lru_cache(maxsize=64)
    @cachedFn()
    @countedFn(name='TMDB (after caching)')
    def __tmdb(self, service, max_retries=3, **params):
        if 'api_key' not in params:
            params['api_key'] = self.__key
        
        pairs = [ '%s=%s' % (k,urllib2.quote(str(v))) for k,v in params.items() ]
        url = 'http://api.themoviedb.org/3/%s?%s' % (service,'&'.join(pairs))
        logs.info(url)
        
        while True:
            try:
                with self.__limiter:
                    req = urllib2.Request(url, headers={ 'Accept' : 'application/json' })
                    response = urllib2.urlopen(req).read()
                    data = json.loads(response)
                    return data
            except HTTPError as e:
                logs.warning('error', exc_info=1)
                
                if e.code == 403 and max_retries > 0:
                    max_retries -= 1
                    sleep(1)
                else:
                    return None

__globalTMDB = None

def globalTMDB():
    global __globalTMDB
    
    if __globalTMDB is None:
        __globalTMDB = TMDB()
    
    return __globalTMDB

def demo(query='Star Trek'):
    db = TMDB()
    pprint(db.movie_search(query))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if len(sys.argv) == 2:
            query = sys.argv[1]
            demo(query)
        else:
            db = TMDB()
            command = sys.argv[1]
            tmdb_id= sys.argv[2]
            commands = {
                'keywords':db.movie_keywords,
                'info':db.movie_info,
                'casts':db.movie_casts,
            }
            if command in commands:
                pprint(commands[command](tmdb_id))
            else:
                print('unknown command: %s' % command)
    else:
        demo()

