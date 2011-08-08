#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils

from AEntityProxy import AEntityProxy
from Geocoder import Geocoder

class GeocoderEntityProxy(AEntityProxy):
    
    def __init__(self, source):
        AEntityProxy.__init__(self, source)
        
        self._geocoder = Geocoder()
    
    def _processItems(self, items):
        utils.log("[%s] processing %d items" % (self, utils.count(items)))
        AEntityProxy._processItems(self, items)
    
    def _transform(self, entity):
        try:
            latLng = (entity.lat, entity.lng)
            
            # if entity is already populated with lat/lng, then return it as-is
            return entity
        except KeyError:
            pass
        
        try:
            # entity has an address and only needs the corresponding geocoded lat/lng
            address = entity.address
            latLng  = self._geocoder.addressToLatLng(address)
            
            if latLng is not None:
                entity.lat = latLng[0]
                entity.lng = latLng[1]
            else:
                # we weren't able to geocode the given address to a valid lat/lng, so 
                # filter this entity from the proxy's output
                return None
        except KeyError:
            # entity is not a place
            pass
        
        return entity

