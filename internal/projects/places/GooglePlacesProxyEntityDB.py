#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from Entity import Entity
from EntityMatcher import EntityMatcher
from ProxyEntityDB import ProxyEntityDB
import Utils

class GooglePlacesProxyEntityDB(ProxyEntityDB):
    
    # maps of entity attribute names to funcs which extract the corresponding 
    # attribute from a Google Places detail response.
    _map = {
        'name'      : lambda src: src['name'], 
        'vicinity'  : lambda src: src['vicinity'], 
        'types'     : lambda src: src['types'], 
        'phone'     : lambda src: src['formatted_phone_number'], 
        'address'   : lambda src: src['formatted_address'], 
        'lat'       : lambda src: src['geometry']['location']['lat'], 
        'lng'       : lambda src: src['geometry']['location']['lng'], 
        'gid'       : lambda src: src['id'], 
        'gurl'      : lambda src: src['url'], 
    }
    
    def __init__(self, targetEntityDB):
        ProxyEntityDB.__init__(self, targetEntityDB, "GooglePlaces")
        
        self._target = targetEntityDB
        self._entityMatcher = EntityMatcher()
    
    def _transformInput(self, entity):
        details = self._entityMatcher.getEntityDetailsFromGooglePlaces(entity)
        
        if details:
            for key, extractFunc in self._map.iteritems():
                entity[key] = extractFunc(details)
                #Utils.log("'%s' => '%s'" % (key, str(entity[key])))

