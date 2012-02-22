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
    import TwitterOAuth as oauth
    import urllib2, urllib
    from urlparse import parse_qsl
    try:
        import json
    except ImportError:
        import simplejson as json
except:
    report()
    raise

class Rdio:
    def __init__(self, key, secret):
        self.__consumer = oauth.Consumer(key,secret)
        self.__client = oauth.Client(self.__consumer)

    def method(self, method, **kwargs):
        kwargs['method'] = method 
        # create the OAuth consumer credentials
        response = self.__client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode(kwargs))
        return json.loads(response[1])
