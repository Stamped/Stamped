#!/usr/bin/python

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

__all__ = ['Rdio']

import Globals
from logs   import report
try:
    from RateLimiter        import RateLimiter, RateException
    import TwitterOAuth     as oauth
    import urllib2, urllib
    from urlparse           import parse_qsl
    from urllib2            import HTTPError
    from errors             import StampedHTTPError
    from urllib import quote_plus
    from django.utils.encoding import iri_to_uri
    import logs
    try:
        import json
    except ImportError:
        import simplejson as json
except:
    report()
    raise


def urlencode_utf8(params):
    return '&'.join(
        (quote_plus(k, safe='/') + '=' + iri_to_uri(v)
            for k, v in params.items()))


class Rdio(object):
    def __init__(self, key='bzj2pmrs283kepwbgu58aw47', secret='xJSZwBZxFp', cps=5, cpd=15000):
        self.__key = key
        self.__secret = secret
        self.__reinit()
        self.__limiter = RateLimiter(cps=cps,cpd=cpd)
    
    def __reinit(self):
        self.__consumer = oauth.Consumer(self.__key,self.__secret)

    def method(self, method, **kwargs):
        kwargs['method'] = method 
        # create the OAuth consumer credentials
        client = oauth.Client(self.__consumer)
        for k,v in kwargs.items():
            if isinstance(v,int) or isinstance(v,float):
                kwargs[k] = str(v)
        urlish = 'http://api.rdio.com/1/ POST %s' % urlencode_utf8(kwargs)
        try:
            with self.__limiter:
                logs.info(urlish)
                response = client.request('http://api.rdio.com/1/', 'POST', urlencode_utf8(kwargs),headers={'Accept-encoding':'gzip'})
        except HTTPError as e:
            raise StampedHTTPError('rdio threw an exception',e.code,e.message)
        status = int(response[0]['status'])
        if status == 200:
            return json.loads(response[1])
        else:
            raise StampedHTTPError('rdio returned a failure response %d' % status ,status , response[1]) 

    def userMethod(self, token, token_secret, method, **kwargs): 
        kwargs['method'] = method 
        access_token = oauth.Token(token, token_secret)   
        client = oauth.Client(self.__consumer, access_token)
        with self.__limiter:
            logs.info('http://api.rdio.com/1/ POST %s' % urllib.urlencode(kwargs))
            response = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode(kwargs))
        return json.loads(response[1])




