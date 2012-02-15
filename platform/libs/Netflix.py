#!/usr/bin/python

"""
Interface for Netflix API


"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs import report

try:
    from utils import getFile
    from threading  import Lock
    import time
    import sys
    import json
    import urllib
    import urllib2
    import oauth
    from gevent             import sleep
    from urllib2            import HTTPError
    from urlparse import urlparse, parse_qsl
    from utils              import getFile
except:
    report()
    raise

# sample request
# http://api.netflix.com/oauth/request_token?oauth_consumer_key=nr5nzej56j3smjra6vtybbvw&oauth_nonce=341594518232226&oauth_signature_method=HMAC-SHA1&oauth_timestamp=1329319210&oauth_version=1.0&oauth_signature=VEnkokRv1OGtcmMa1U0%2BVtvDF%2Bg%3D

class Netflix(object):

    def __init__(self):
        self.__key = 'nr5nzej56j3smjra6vtybbvw'
        self.__secret = 'H5A633JsYk'
        self.__lock = Lock()
        self.__last_call = time.time()
        self.__cooldown = .10

    def search(self, term):
        return self.__netflix('research_token',term=term)

    def __netflix(self,service,prefix='oauth',**args):
        """
        Helper method for making OAuth Factual API calls.

        This code is based on the recommended Python sample code available at:

        http://developer.factual.com/display/docs/Core+API+-+Oauth

        The custom beginning constructs the url based on input parameters.

        The custom end parses the JSON response and abstracts the data portion if successful.
        """
        args['nounce'] ='123sdfasf'
        args['oauth_signature_method'] = 'HMAC-SHA1'
        args['oauth_timestamp'] = int(time.time())
        args['oauth_version'] = '1.0'
        pairs = [ '%s=%s' % (k,v) for k,v in args.items() ]
        url =  "https://api.netflix.com/%s/%s?%s" % (prefix,service,'&'.join(pairs))
        params    = parse_qsl(urlparse(url).query)
        consumer  = oauth.OAuthConsumer(key=self.__key, secret=self.__secret)
        request   = oauth.OAuthRequest.from_request(http_method='GET', http_url=url,parameters=args)
        signature = oauth.OAuthSignatureMethod_HMAC_SHA1().build_signature( request ,consumer, None)
        url = url+"&oauth_signature="+urllib.quote(signature)
        print(url)
        print(request.to_header())
        with self.__lock:
            elapsed = time.time() - self.__last_call
            #in case of error, set last call
            self.__last_call = time.time()
            cooldown = self.__cooldown - elapsed
            if cooldown > 0:
                sleep(cooldown)
            response = getFile(url)
            self.__last_call = time.time()
        m = json.loads(response)
        try:
            return m['response']['data']
        except:
            return None


    def __factual(self,service,prefix='oauth',**args):
        """
        Helper method for making OAuth Factual API calls.

        This code is based on the recommended Python sample code available at:

        http://developer.factual.com/display/docs/Core+API+-+Oauth

        The custom beginning constructs the url based on input parameters.

        The custom end parses the JSON response and abstracts the data portion if successful.
        """
        pairs = [ '%s=%s' % (k,v) for k,v in args.items() ]
        url =  "https://api.netflix.com/%s/%s?%s" % (prefix,service,'&'.join(pairs))
        params    = parse_qsl(urlparse(url).query)
        consumer  = oauth.OAuthConsumer(key=self.__key, secret=self.__secret)
        request   = oauth.OAuthRequest.from_consumer_and_token(consumer, http_method='GET', http_url=url, parameters=params)

        request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), consumer, None)

        with self.__lock:
            elapsed = time.time() - self.__last_call
            #in case of error, set last call
            self.__last_call = time.time()
            cooldown = self.__cooldown - elapsed
            if cooldown > 0:
                sleep(cooldown)
            req = urllib2.Request(url, None, request.to_header())
            res = urllib2.urlopen(req)
            response = res.read()
            self.__last_call = time.time()
        m = json.loads(response)
        try:
            return m['response']['data']
        except:
            return None


if __name__ == "__main__":
    n = Netflix()
    print(n.search('StarTrek'))
    
