#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import base64, hashlib, hmac
import json, urllib, urllib2, utils
import sys


from pprint import pprint

class SinglePlatform(object):
    """
        Lightweight wrapper around SinglePlatform API.
    """
    
    BASE_URL = "http://api.singleplatform.co"
    
    def __init__(self, client_id, signing_key, api_key=None):
        assert client_id   is not None and len(client_id)   > 0
        assert signing_key is not None and len(signing_key) > 0
        
        self._client_id   = client_id
        self._api_key     = api_key
        
        padding_factor    = (4 - len(signing_key) % 4) % 4
        signing_key      += "=" * padding_factor
        
        self._signing_key = base64.b64decode(unicode(signing_key).translate(dict(zip(map(ord, u'-_'), u'+/'))))
    
    def search(self, query, page=0, count=20):
        params = {
            'q'     : query, 
            'page'  : page, 
            'count' : count, 
        }
        
        return self._get_uri('/restaurants/search', params)
    
    def lookup(self, location_id):
        return self._get_uri('/restaurants/%s' % location_id)
    
    def get_menu(self, location_id):
        return self._get_uri('/restaurants/%s/menu' % location_id)
    
    def get_short_menu(self, location_id):
        return self._get_uri('/restaurants/%s/shortmenu' % location_id)
    
    #TODO implement
    def get_stamped_menu(self,location_id):
        pass

    def _get_uri(self, uri, params=None):
        if params is not None:
            uri = "%s?%s" % (uri, urllib.urlencode(params))
        
        # construct the signed url
        uri = "%s%sclient=%s" % (uri, '?' if params is None else '&', self._client_id)
        uri = uri.encode('utf-8')
        url = "%s%s&sig=%s" % (self.BASE_URL, uri, self._sign(uri))
        
        request = urllib2.Request(url)
        request.add_header('Accept-encoding', 'gzip')
        request.add_header('Accept', 'application/json')
        
        return json.loads(utils.getFile(url, request))
    
    def _sign(self, uri):
        digest = hmac.new(self._signing_key, uri, hashlib.sha1).digest()
        digest = base64.urlsafe_b64encode(digest)
        digest = digest.rstrip('=')
        
        return digest

class StampedSinglePlatform(SinglePlatform):
    def __init__(self):
        SinglePlatform.__init__(self, 
                                client_id='cyibvntpqlfgmsnynncnkbscg', 
                                signing_key='1THU8A8TPUYw84LIXQTomgZNNx4yoKnQiDpNv9yDPuQ', 
                                api_key='kpm48ecj0bb5zai7qc5wvq562')

if __name__ == '__main__':
    sp = StampedSinglePlatform()
    if len(sys.argv) > 1:
        import Factual
        f = Factual.Factual()
        sp_id = f.singleplatform(sys.argv[1])
        print(sp_id)
        results = sp.get_menu(sp_id)
        pprint(results)
    else:
        # Search for Nobu NY by its phone number
        #results = sp.search(query='2122190500')
        results = sp.get_menu('nobu')
        pprint(results)

