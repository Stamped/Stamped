#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs   import report
try:
    import sys
    import json
    import urllib2
    from logs       import log
    from utils      import getFile
    from urllib2    import HTTPError
    from gevent     import sleep
    from pprint     import pprint
except:
    report()
    raise

class TVDB(object):

    def __init__(self):
        self.__key = 'b4aaa79e39e12f8d066903b8574ee538'

    def configuration(self):
        return self.__tmdb('configuration')

    def person_search(self, query, page=1):
        return self.__tmdb('search/person',query=query,page=page)

    def person_credits(self, tvdb_id):
        return self.__tmdb('person/%s/credits' %(tvdb_id,))

    def person_images(self, tvdb_id):
        return self.__tmdb('person/%s/images' %(tvdb_id,))

    def movie_latest(self, query, page=1):
        return self.__tmdb('latest/movie',query=query,page=page)

    def movie_search(self, query, page=1):
        return self.__tmdb('search/movie',query=query,page=page)

    def movie_info(self, tvdb_id):
        return self.__tmdb('movie/%s' %(tvdb_id,))

    def movie_casts(self, tvdb_id):
        return self.__tmdb('movie/%s/casts' %(tvdb_id,))

    def movie_keywords(self, tvdb_id):
        return self.__tmdb('movie/%s/keywords' %(tvdb_id,))
    
    def movie_alternative_titles(self, tvdb_id):
        return self.__tmdb('movie/%s/alternative_titles' %(tvdb_id,))

    def movie_images(self, tvdb_id):
        return self.__tmdb('movie/%s/images' %(tvdb_id,))

    def movie_releases(self, tvdb_id):
        return self.__tmdb('movie/%s/releases' %(tvdb_id,))

    def movie_trailers(self, tvdb_id):
        return self.__tmdb('movie/%s/trailers' %(tvdb_id,))

    def movie_translations(self, tvdb_id):
        return self.__tmdb('movie/%s/translations' %(tvdb_id,))

    def collection_info(self, tvdb_id):
        return self.__tmdb('collection/%s' %(tvdb_id,))

    def __tmdb(self,service,max_retries=3,**params):
        if 'api_key' not in params:
            params['api_key'] = self.__key
        pairs = [ '%s=%s' % (k,urllib2.quote(str(v))) for k,v in params.items() ]
        url = 'http://api.themoviedb.org/3/%s?%s' % (service,'&'.join(pairs))
        log.info(url)
        try:
            req = urllib2.Request(url,headers={ 'Accept' : 'application/json' })
            response = urllib2.urlopen(req).read()
            data = json.loads(response)
            return data
        except HTTPError as e:
            log.warning('error',exc_info=1)
            if e.code == 403:
                sleep(1)
                if max_retries > 0:
                    return self.__tmdb(service,max_retries-1,**params)
                else:
                    return None
            else:
                return None

def demo(query='Star Trek'):
    db = TVDB()
    pprint(db.movie_search(query))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if len(sys.argv) == 2:
            query = sys.argv[1]
            demo(query)
        else:
            db = TVDB()
            command = sys.argv[1]
            other = sys.argv[2]
            if command == 'keywords':
                pprint(db.movie_keywords(other))
            if command == 'info':
                pprint(db.movie_info(other))
            else:
                print('unknown command: %s' % command)
    else:
        demo()
    
    
