#!/usr/bin/env python
"""

"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import base64, hashlib, hmac
import json, urllib
import datetime, logs, sys, time

from pprint         import pprint
from libs.LRUCache       import lru_cache
from libs.Memcache       import memcached_function
from api.Schemas    import Menu
from api.Schemas    import Submenu
from api.Schemas    import MenuSection
from api.Schemas    import MenuItem
from api.Schemas    import MenuPrice
from threading      import Lock
from libs.Request   import service_request
from APIKeys        import get_api_key

CLIENT_ID   = get_api_key('singleplatform', 'client_id')
SIGNING_KEY = get_api_key('singleplatform', 'signing_key')
API_KEY     = get_api_key('singleplatform', 'api_key')

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
        p2 = MenuPrice()
        p2.title = p['title']
        p2.price = p['price']
        p2.unit = p['unit']
        p2.currency = 'dollars'
        prices.append(p2)
    return prices


def _parseMenu(menu):
    m = Submenu()
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
            cur_section = MenuSection()
            sections.append(cur_section)
            cur_section.title = entry['title']
            cur_section.desc = entry['desc']
        elif t == 'item':
            item = MenuItem()
            item.title = entry['title']
            item.desc = entry['desc']
            item.spicy = _parse_spicy(entry)
            item.allergens = entry['allergens']
            item.allergen_free = entry['allergenFree']
            item.restrictions = entry['restrictions']
            item.prices = _parse_prices(entry)
            cur_items.append(item)
    if not cur_section:
        cur_section =  MenuSection()
    cur_section.items = cur_items
    m.sections = sections
    return m

def toMenu(menu):
    if not menu:
        return None
    schema = Menu()
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
    
    def search(self, query, page=0, count=20, priority='low'):
        params = {
            'q'     : query, 
            'page'  : page, 
            'count' : count, 
        }
        
        return self._get_uri('/restaurants/search', priority, params)
    
    def lookup(self, location_id, priority='low'):
        return self._get_uri('/restaurants/%s' % location_id, priority)
    
    def get_menu(self, location_id, priority='low'):
        return self._get_uri('/restaurants/%s/menu' % location_id, priority)

    def get_menu_schema(self, location_id, priority='low'):
        return toMenu(self.get_menu(location_id, priority))
    
    def get_short_menu(self, location_id, priority='low'):
        return self._get_uri('/restaurants/%s/shortmenu' % location_id, priority)
    
    def _get_uri(self, uri, priority='low', params=None):
        if params is not None:
            uri = "%s?%s" % (uri, urllib.urlencode(params))
        
        # construct the signed url
        uri = "%s%sclient=%s" % (uri, '?' if params is None else '&', self._client_id)
        uri = uri.encode('utf-8')
        url = "%s%s&sig=%s" % (self.BASE_URL, uri, self._sign(uri))

        header = {
            'Accept-encoding': 'gzip',
            'Accept' : 'application/json',
        }
        response, content = service_request('singleplatform', 'GET', url, header=header, priority=priority)
        logs.info(url)
        result = json.loads(content)
        return result
    
    def _sign(self, uri):
        digest = hmac.new(self._signing_key, uri, hashlib.sha1).digest()
        digest = base64.urlsafe_b64encode(digest)
        digest = digest.rstrip('=')
        
        return digest

class StampedSinglePlatform(SinglePlatform):
    def __init__(self):
        SinglePlatform.__init__(self, 
                                client_id=CLIENT_ID,
                                signing_key=SIGNING_KEY,
                                api_key=API_KEY)

if __name__ == '__main__':
    sp = StampedSinglePlatform()
    if len(sys.argv) > 1:
        from libs import Factual
        f = Factual.Factual()
        sp_id = f.singleplatform(sys.argv[1])
        print(sp_id)
        results = sp.get_menu(sp_id)
        #pprint(results)
        results = toMenu(results)
        pprint(results)
    else:
        # Search for Nobu NY by its phone number
        #results = sp.search(query='2122190500')
        results = sp.get_menu('nobu')
        pprint(results)

