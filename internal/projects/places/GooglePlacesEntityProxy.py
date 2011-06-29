#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, Utils

from EntityMatcher import EntityMatcher
from AEntityProxy import AEntityProxy

class GooglePlacesEntityProxy(AEntityProxy):
    
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
    
    def __init__(self, source):
        AEntityProxy.__init__(self, source, "GooglePlaces")
        
        self._entityMatcher = EntityMatcher()
    
    def _transform(self, entity):
        details = self._entityMatcher.getEntityDetailsFromGooglePlaces(entity)
        
        if details is not None:
            for key, extractFunc in self._map.iteritems():
                try:
                    value = extractFunc(details)
                    entity[key] = value
                except KeyError:
                    pass
                #Utils.log("'%s' => '%s'" % (key, str(entity[key])))
        
        return entity

