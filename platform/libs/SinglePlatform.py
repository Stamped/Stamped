#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import base64, hashlib, hmac
import json, urllib, urllib2, utils

from pprint import pprint

class SinglePlatform(object):
    """
        Lightweight wrapper around SinglePlatform restaurant API.
    """
    
    BASE_URL = "http://api.singleplatform.co"
    
    def __init__(self, client_id, signing_key):
        assert client_id   is not None and len(client_id)   > 0
        assert signing_key is not None and len(signing_key) > 0
        
        self._client_id   = client_id
        self._signing_key = signing_key
    
    def search(self, query, page=0, count=20):
        params = {
            'q'     : query, 
            'page'  : page, 
            'count' : count, 
        }
        
        return self._get_uri('/restaurants/search', params)
    
    def lookup(self, location_id):
        # TODO: docs are inconsistent w.r.t. slash after location_id...
        return self._get_uri('/restaurants/%s' % location_id)
    
    def _get_uri(self, uri, params=None):
        if params is not None:
            uri = "%s?%s" % (uri, urllib.urlencode(params))
        
        uri = "%s%sclient=%s" % (uri, '?' if params is None else '&', self._client_id)
        uri = uri.encode('utf-8')
        url = "%s/%s&sig=%s" % (self.BASE_URL, uri, self._sign(uri))
        
        utils.log(url)
        return None
        
        request = urllib2.Request(url)
        request.add_header('Accept-encoding', 'gzip')
        request.add_header('Accept', 'application/json')
        
        return json.loads(utils.getFile(url, request))
    
    def _sign(self, uri):
        # see http://www.doughellmann.com/PyMOTW/hmac/
        return base64.urlsafe_b64encode(hmac.new(self._signing_key, uri, hashlib.sha1).digest())

if __name__ == '__main__':
    sp = SinglePlatform(client_id='stamped', signing_key='test')
    
    # Search for Nobu NY by its phone number
    results = sp.search(query='2122190500')
    pprint(results)

