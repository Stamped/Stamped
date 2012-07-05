#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from crawler.match.ATitleBasedEntityMatcher import ATitleBasedEntityMatcher
from libs.GooglePlaces             import GooglePlaces
from Schemas                  import Entity
from errors                   import Fail

class GooglePlacesEntityCrossReference(ATitleBasedEntityMatcher):
    def __init__(self, stamped_api, options):
        ATitleBasedEntityMatcher.__init__(self, stamped_api, options)
        self._googlePlaces = GooglePlaces()
    
    def getDuplicateCandidates(self, entity):
        coords = [ entity.lat, entity.lng ]
        google_results = self._googlePlaces.getEntityResultsByLatLng(coords, params, False)
        
        return google_results
    
    def getMatchingDuplicates(self, entity, candidate_entities):
        dupes = ATitleBasedEntityMatcher.getMatchingDuplicates(self, entity, candidate_entities)
        
        for dupe in dupes:
            if 'reference' in dupe:
                details = self._googlePlaces.getPlaceDetails(dupe['reference'])
                
                if details is not None:
                    if 'formatted_phone_number' in details:
                        dupe.phone = details['formatted_phone_number']
                    if 'formatted_address' in details:
                        dupe.address = details['formatted_address']
                    if 'address_components' in details:
                        dupe.address_components = details['address_components']
        
        return dupes

