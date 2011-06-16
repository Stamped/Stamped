#!/usr/bin/python

import json, re, urllib, Utils

from difflib import SequenceMatcher
from Geocoder import Geocoder

class GooglePlaces(object):
    API_KEY  = 'AIzaSyAxgU3LPU-m5PI7Jh7YTYYKAz6lV6bz2ok'
    BASE_URL = 'https://maps.googleapis.com/maps/api/place'
    FORMAT   = 'json'
    RADIUS   = 500 # meters
    
    def __init__(self, log):
        self._geocoder = Geocoder()
        self.log = log
        pass
    
    def tryMatchEntity(self, entity):
        latLng = self._geocoder.addressToLatLng(entity['address'])
        
        if latLng is None or latLng[0] is None or latLng[1] is None:
            # geocoding translation from address to lat/lng failed, so we will 
            # be unable to cross-reference this entity with google places.
            return None
        
        params = {
            'location'  : str(latLng[0]) + ',' + str(latLng[1]), 
            'name'      : entity['name'], 
            'radius'    : self.RADIUS, 
            'sensor'    : 'false', 
            'key'       : self.API_KEY
        }
        
        # example URL:
        # https://maps.googleapis.com/maps/api/place/search/json?location=-33.8670522,151.1957362&radius=500&types=food&name=harbour&sensor=false&key=AIzaSyAxgU3LPU-m5PI7Jh7YTYYKAz6lV6bz2ok
        url = self.getAPIURL('search', params)
        self.log(url)
        
        try:
            # GET the data and parse the response as json
            response = json.loads(Utils.GetFile(url))
            
            # ensure that we received a valid response
            if response['status'] != 'OK':
                self.log('[GooglePlaces] error searching "' + url + '"\n' + 
                         'ErrorCode: ' + response['status'] + '\n')
                return None
            
            results = response['results']
            if len(results) <= 0:
                self.log('[GooglePlaces] error searching "' + url + '"\n' + 
                         'Zero results returned\n')
                return None
            
            # perform case-insensitive, fuzzy string matching to determine the 
            # best match in the google places result set for the target entity
            bestRatio  = -1
            bestMatch  = None
            entityName = entity['name'].lower()
            
            for result in results:
                # TODO: alternatively look into using edit distance via:
                #       http://code.google.com/p/pylevenshtein/
                matcher = SequenceMatcher(None, entityName, result['name'].lower())
                ratio = matcher.ratio()
                
                if ratio > bestRatio:
                    bestRatio = ratio
                    bestMatch = result
            
            self.log(bestRatio)
            # if no results matched the entity at all, then disregard the 
            # results as irrelevant and return empty-handed
            if bestRatio <= 0:
                return None
            
            # otherwise, we have a match!
            # TODO: place a details query to obtain detailed info for the match
            return bestMatch
        except:
            self.log('[GooglePlaces] unexpected error searching "' + url + '"')
            return None
        
        return None
    
    def getAPIURL(self, method, params):
        return self.BASE_URL + '/' + method + '/' + self.FORMAT + '?' + urllib.urlencode(params)

