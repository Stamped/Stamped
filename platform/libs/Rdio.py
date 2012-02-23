#!/usr/bin/python

"""
Rdio wrapper

Notes:
to get tracks in playlists use: extras='trackKeys'

Sample user key (don't use much, it's mine -Landon)
('dnrkqfbtek39678h37y5u2ke38rzxvkeywfhgsbqn8s9z45rx9mjrmagcds6cf3w', 'fpdNE4EgBHgz')
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs   import report
try:
    import TwitterOAuth as oauth
    import urllib2, urllib
    from urlparse import parse_qsl
    import logs
    try:
        import json
    except ImportError:
        import simplejson as json
except:
    report()
    raise

class Rdio:
    def __init__(self, key='bzj2pmrs283kepwbgu58aw47', secret='xJSZwBZxFp'):
        self.__key = key
        self.__secret = secret
        self.__reinit()
    
    def __reinit(self):
        self.__consumer = oauth.Consumer(self.__key,self.__secret)

    def method(self, method, **kwargs):
        kwargs['method'] = method 
        # create the OAuth consumer credentials
        client = oauth.Client(self.__consumer)
        logs.info('http://api.rdio.com/1/ POST %s' % urllib.urlencode(kwargs))
        response = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode(kwargs))
        return json.loads(response[1])

    def userMethod(self, token, token_secret, method, **kwargs): 
        kwargs['method'] = method 
        access_token = oauth.Token(token, token_secret)   
        client = oauth.Client(self.__consumer, access_token)
        logs.info('http://api.rdio.com/1/ POST %s' % urllib.urlencode(kwargs))
        response = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode(kwargs))
        return json.loads(response[1])