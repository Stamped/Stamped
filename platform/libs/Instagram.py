#!/usr/bin/env python
from __future__ import absolute_import

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


__all__ = ['Instagram', 'globalInstagram']

import Globals
import httplib
from libs import oauth as oauth
from logs   import report
try:
    import sys
    import json
    import urllib2
    import logs

    from urllib2        import HTTPError
    from gevent         import sleep
    from pprint         import pprint
    from libs.RateLimiter    import RateLimiter, RateException
    from libs.LRUCache       import lru_cache
    from libs.Memcache       import memcached_function
    from libs.Request        import service_request
    from APIKeys import get_api_key
except:
    report()
    raise

HOST            = 'https://api.instagram.com/v1'
PORT            = '80'
CLIENT_ID       = get_api_key('instagram', 'client_id')
CLIENT_SECRET   = get_api_key('instagram', 'client_secret')

class Instagram(object):
    def __init__(self, client_id=CLIENT_ID, client_secret=CLIENT_SECRET):
        self.__client_id=client_id
        self.__client_secret=client_secret
        self.__consumer = oauth.OAuthConsumer(self.__client_id, self.__client_secret)
        self.__signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()

    #def place_search(self, **kwargs):
    #    return self.__instagram('locations/search', **kwargs)

    def place_search(self, foursquare_id, priority='low', timeout=None):
        return self.__instagram('locations/search', priority, timeout, foursquare_v2_id=foursquare_id)

    def place_lookup(self, instagram_id, priority='low', timeout=None):
        return self.__instagram('locations/' + instagram_id, priority, timeout)

    def place_recent_media(self, instagram_id, priority='low', timeout=None):
        return self.__instagram('locations/%s/media/recent' % instagram_id, priority, timeout)

#    def place_recent_media(self, **kwargs):
#        return self.

    # note: these decorators add tiered caching to this function, such that
    # results will be cached locally with a very small LRU cache of 64 items
    # and also cached remotely via memcached with a TTL of 7 days
#    @lru_cache(maxsize=64)
#    @memcached_function(time=7*24*60*60)
    def __instagram(self, service, priority='low', timeout=None, max_retries=3, verb='GET', **params):
        if 'client_id' not in params:
            params['client_id'] = self.__client_id

        if service.startswith('http'):
            url = service
        else:
            url = "%s/%s" % (HOST, service)

        response, content = service_request('instagram',
                                            'GET',
                                            url,
                                            query_params=params,
                                            header={ 'Accept' : 'application/json' },
                                            priority=priority,
                                            timeout=timeout)

        data = json.loads(content)
        return data

__globalInstagram = None

def globalInstagram():
    global __globalInstagram

    if __globalInstagram is None:
        __globalInstagram = Instagram()

    return __globalInstagram

def demo(foursquare_id, **params):
    instagram = Instagram()
    place = instagram.place_search(foursquare_id)
    recent_media = instagram.place_recent_media(place['data'][0]['id'])
    pprint(recent_media)


if __name__ == '__main__':
    import sys
    params = {}
    foursquare_id = '4d1bb4017e10a35d5737f982'
    if len(sys.argv) > 1:
        foursquare_id = sys.argv[1]
    if len(sys.argv) > 2:
        params = {}
        for arg in sys.argv[2:]:
            pair = arg.split('=')
            params[pair[0]] = pair[1]
    demo(foursquare_id, **params)

