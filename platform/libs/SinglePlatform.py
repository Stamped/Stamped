#!/usr/bin/env python
"""

"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import base64, hashlib, hmac
import json, urllib, urllib2, utils
import datetime, logs, sys, time

from pprint         import pprint
from LRUCache       import lru_cache
from Memcache       import memcached_function
from Schemas        import MenuSchema
from Schemas        import SubmenuSchema
from Schemas        import MenuSectionSchema
from Schemas        import MenuItemSchema
from Schemas        import MenuPriceSchema
from urllib2        import HTTPError
from threading      import Lock
from gevent         import sleep

_spicy_map = {
    'none':0,
    'mild':1,
    'medium':2,
    'hot':3,
}

def _parse_spicy(entry):
    if 'spicy' in entry:
        v = entry['spicy']
        if v in _spicy_map:
            return _spicy_map[v]
    return None

def _parse_prices(entry):
    prices = []
    for p in entry['prices']:
        p2 = MenuPriceSchema()
        p2.title = p['title']
        p2.price = p['price']
        p2.unit = p['unit']
        p2.currency = 'dollars'
        prices.append(p2)
    return prices


def _parseMenu(menu):
    m = SubmenuSchema()
    m.title = menu['title']
    # TODO times
    m.footnote = menu['footnote']
    m.desc = menu['desc']
    sections = []
    cur_section = None
    cur_items = []
    for entry in menu['entries']:
        t = entry['type']
        if t == 'section':
            if cur_section:
                cur_section.items = cur_items
                cur_items = []
            cur_section = MenuSectionSchema()
            sections.append(cur_section)
            cur_section.title = entry['title']
            cur_section.desc = entry['desc']
        elif t == 'item':
            item = MenuItemSchema()
            item.title = entry['title']
            item.desc = entry['desc']
            item.spicy = _parse_spicy(entry)
            item.allergens = entry['allergens']
            item.allergen_free = entry['allergenFree']
            item.restrictions = entry['restrictions']
            item.prices = _parse_prices(entry)
            cur_items.append(item)
    if not cur_section:
        cur_section =  MenuSectionSchema()
    cur_section.items = cur_items
    m.sections = sections
    return m

def toMenuSchema(menu):
    if not menu:
        return None
    schema = MenuSchema()
    schema.source = 'singleplatform'
    schema.source_id = menu['location']['id']
    schema.timestamp = datetime.datetime.utcnow()
    menus = menu['menus']
    if len(menus) == 0:
        return None
    first_menu = menus[0]
    schema.disclaimer = first_menu['disclaimer']
    schema.attribution_image = first_menu['attributionImage']
    schema.attribution_image_link = first_menu['attributionImageLink']
    schema.menus = [ _parseMenu(m) for m in menus]
    return schema

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
        self.__lock = Lock()
        self.__last_call = time.time()
        self.__cooldown = .4
        self.__throttled = 0
    
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

    def get_menu_schema(self, location_id):
        return toMenuSchema(self.get_menu(location_id))
    
    def get_short_menu(self, location_id):
        return self._get_uri('/restaurants/%s/shortmenu' % location_id)
    
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
        logs.info(url)
        result = None
        try:
            with self.__lock:
                if self.__throttled > 5:
                    raise HTTPError(url,403,'Internal rate limit exceeded',None,None)
                elapsed = time.time() - self.__last_call
                self.__last_call = time.time()
                cooldown = self.__cooldown - elapsed
                if cooldown > 0:
                    sleep(cooldown)
                result = json.loads(utils.getFile(url, request))
                self.__last_call = time.time()
        except HTTPError as e:
            if e.code == 403:
                self.__throttled += 1
                sleep(1)
            raise
        return result
    
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
        #pprint(results)
        results = toMenuSchema(results)
        pprint(results)
    else:
        # Search for Nobu NY by its phone number
        #results = sp.search(query='2122190500')
        results = sp.get_menu('nobu')
        pprint(results)

