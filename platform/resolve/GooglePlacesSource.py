#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'GooglePlacesSource' ]

import Globals
from logs import report

try:
    from BasicSource            import BasicSource
    from GooglePlaces           import GooglePlaces
    from utils                  import lazyProperty
    from datetime               import datetime
    from functools              import partial
    from LibUtils               import states
except:
    report()
    raise

def _path(path,data):
    cur = data
    for k in path:
        if k in cur:
            cur = cur[k]
        else:
            return None
    return cur

def _ppath(*args):
    return partial(_path,args)

def _constant_helper(value,not_used):
    return value

def _constant(value):
    return partial(_constant_helper,value)

class GooglePlacesSource(BasicSource):
    """
    Data-Source wrapper for Google Places.
    """
    def __init__(self):
        BasicSource.__init__(self, 'googleplaces',

            'address',
            'phone',
            'site',
            'neighborhood',
        )

    @lazyProperty
    def __places(self):
        return GooglePlaces()
    
    def enrichEntity(self, entity, controller, decorations, timestamps):
        details = self.__details(entity)
        if details is None:
            return False

        reformatted = self.__reformatAddress(details)
        if reformatted is not None:
            self.writeFields(entity, None, reformatted)

        neighborhood = self.__neighborhood(details)
        if neighborhood is not None:
            entity['neighborhood'] = neighborhood
    
        if 'formatted_phone_number' in details and details['formatted_phone_number'] != '':
            entity['phone'] = details['formatted_phone_number']
    
        if 'website' in details and details['website'] != '':
            entity['site'] = details['website']
        return True

    def __details(self, entity):
        try:
            details = None
            if 'lng' in entity and 'lat' in entity and 'title' in entity:
                gdata = self.__places.getSearchResultsByLatLng((entity['lat'],entity['lng']),{'name':entity['title']})
                if gdata is not None and len(gdata) > 0:
                    gdatum = gdata[0]
                    if 'reference' in gdatum:
                        ref = gdatum['reference']
                        details = self.__places.getPlaceDetails(ref)
            return details
        except:
            return None

    def __neighborhood(self, details):
        locality = None
        sublocality = None
        if 'address_components' in details:
            for comp in details['address_components']:
                if 'types' in comp and 'long_name' in comp:
                    name = comp['long_name']
                    types = comp['types']
                    if 'locality' in types:
                        locality = name
                    elif 'sublocality' in types:
                        sublocality = name
        if locality is not None and sublocality is not None:
            return sublocality
        else:
            return None

    def __reformatAddress(self, results):
        if 'address_components' not in results:
            return None
        data = {
            'address_street':None,
            'address_street_ext':None,
            'address_locality':None,
            'address_region':None,
            'address_postcode':None,
            'address_country':None,
        }
        number = None
        route = None
        for comp in results['address_components']:
            if 'types' in comp and 'long_name' in comp:
                name = comp['long_name']
                types = comp['types']
                if 'administrative_area_level_1' in types:
                    #TODO consider country checking
                    if name in states:
                        name = states[name]
                    data['address_region'] = name
                elif 'country' in types:
                    data['address_country'] = name
                elif 'postal_code' in types:
                    data['address_postcode'] = name
                elif 'locality' in types:
                    data['address_locality'] = name
                elif 'street_number' in types:
                    number = name
                elif 'route' in types:
                    route = name
        for comp in results['address_components']:
            if 'types' in comp and 'long_name' in comp:
                name = comp['long_name']
                types = comp['types']
                if 'sublocality' in types and data['address_locality'] is None:
                    data['address_locality'] = name
        if route is not None and number is not None:
            data['address_street'] = "%s %s" % (number, route)
        data2 = {}
        for k,v in data.items():
            data2[tuple(k.split('.'))] = _constant(v)
        return data2
    

