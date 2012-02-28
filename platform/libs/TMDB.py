#!/usr/bin/python

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
    from utils      import getFile
    from urllib2    import HTTPError
    from gevent     import sleep
    from pprint     import pprint
    from RateLimiter            import RateLimiter, RateException
except:
    report()
    raise

class TMDB(object):

    def __init__(self):
        self.__key = 'b4aaa79e39e12f8d066903b8574ee538'
        self.__limiter = RateLimiter(cps=10)

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

    def __tmdb(self,service,max_retries=3,**params):
        if 'api_key' not in params:
            params['api_key'] = self.__key
        pairs = [ '%s=%s' % (k,urllib2.quote(str(v))) for k,v in params.items() ]
        url = 'http://api.themoviedb.org/3/%s?%s' % (service,'&'.join(pairs))
        logs.info(url)
        try:
            with self.__limiter:
                req = urllib2.Request(url,headers={ 'Accept' : 'application/json' })
                response = urllib2.urlopen(req).read()
                data = json.loads(response)
                return data
        except HTTPError as e:
            logs.warning('error',exc_info=1)
            if e.code == 403:
                sleep(1)
                if max_retries > 0:
                    return self.__tmdb(service,max_retries-1,**params)
                else:
                    return None
            else:
                return None

_globalTMDB = TMDB()

def globalTMDB():
    return _globalTMDB

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
    
    
