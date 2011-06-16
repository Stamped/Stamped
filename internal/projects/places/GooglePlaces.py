#!/usr/bin/python

import json, re, sys, urllib, Utils

from optparse import OptionParser
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
    
    def getSearchResultsByAddress(self, address, optionalParams={}):
        latLng = self._addressToLatLng(address)
        
        if latLng is None:
            # geocoding translation from address to lat/lng failed, so we will 
            # be unable to cross-reference this address with google places.
            return None
        
        return self.getSearchResultsByLatLng(latLng, optionalParams)
    
    def getSearchResultsByLatLng(self, latLng, optionalParams={}):
        response = self.getSearchResponseByLatLng(latLng, optionalParams)
        
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
        
        return results
    
    def getSearchResponseByAddress(self, address, optionalParams={}):
        latLng = self._addressToLatLng(address)
        
        if latLng is None:
            # geocoding translation from address to lat/lng failed, so we will 
            # be unable to cross-reference this address with google places.
            return None
        
        return self.getSearchResponseByLatLng(latLng, optionalParams)
    
    def getSearchResponseByLatLng(self, latLng, optionalParams={}):
        params = {
            'location'  : self._geocoder.getEncodedLatLng(latLng), 
            'radius'    : self.RADIUS, 
            'sensor'    : 'false', 
            'key'       : self.API_KEY
        }
        
        for key in optionalParams:
            params[key] = optionalParams[key]
        
        # example URL:
        # https://maps.googleapis.com/maps/api/place/search/json?location=-33.8670522,151.1957362&radius=500&types=food&name=harbour&sensor=false&key=AIzaSyAxgU3LPU-m5PI7Jh7YTYYKAz6lV6bz2ok
        url = self._getAPIURL('search', params)
        self.log(url)
        
        try:
            # GET the data and parse the response as json
            return json.loads(Utils.getFile(url))
        except:
            self.log('[GooglePlaces] unexpected error searching "' + url + '"')
            return None
        
        return None
    
    def tryMatchEntity(self, entity):
        try:
            results = self.getSearchResultsByAddress(entity['address'], { 'name' : entity['name'] })
            
            if results is None:
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
    
    def _getAPIURL(self, method, params):
        return self.BASE_URL + '/' + method + '/' + self.FORMAT + '?' + urllib.urlencode(params)
    
    def _addressToLatLng(self, address):
        latLng = self._geocoder.addressToLatLng(address)
        
        if latLng is None or latLng[0] is None or latLng[1] is None:
            # geocoding translation from address to lat/lng failed
            return None
        
        return latLng

def parseCommandLine():
    usage   = "Usage: %prog [options] address|latLng"
    version = "%prog 1.0"
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-a", "--address", action="store_true", dest="address", 
        default=True, help="Parse the argument as an address")
    parser.add_option("-b", "--latLng", action="store_false", dest="address", 
        default=False, help="Parse the argument as an encoded latitude/longitude pair (e.g., '40.144729,-74.053527')")
    parser.add_option("-n", "--name", action="store", type="string", dest="name", 
        default=None, help="Optionally provide a name to filter results")
    parser.add_option("-r", "--radius", action="store", type="int", dest="radius", 
        default=500, help="Optionally specify a radius")
    parser.add_option("-l", "--limit", action="store", type="int", dest="limit", 
        default=None, help="Limit the number of results shown to the top n results")
    
    parser.set_defaults(address=True)
    parser.set_defaults(name=None)
    parser.set_defaults(limit=None)
    parser.set_defaults(radius=500)
    
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.print_help()
        return None
    
    return (options, args)

def main():
    """
        Usage: GooglePlaces.py [options] address|latLng

        Options:
          -h, --help            show this help message and exit
          -a, --address         Parse the argument as an address
          -b, --latLng          Parse the argument as an encoded latitude/longitude
                                pair (e.g., '40.144729,-74.053527')
          -n NAME, --name=NAME  Optionally provide a name to filter results
          -r RADIUS, --radius=RADIUS
                                Optionally specify a radius
          -l LIMIT, --limit=LIMIT
                                Limit the number of results shown to the top n results
    """
    
    result = parseCommandLine()
    if result is None:
        sys.exit(0)
    
    (options, args) = result
    
    places = GooglePlaces(Utils.log)
    results = []
    optionalParams = {}
    
    if options.name:
        optionalParams['name'] = options.name
    if options.radius:
        optionalParams['radius'] = options.radius
    
    if options.address:
        results = places.getSearchResultsByAddress(args[0], optionalParams)
    else:
        results = places.getSearchResultsByLatLng(args[0], optionalParams)
    
    if results is None:
        print "Failed to return results for '%s'" % (args[0], )
    else:
        if options.limit:
            results = results[0:min(options.limit, len(results))]
        
        # print the prettified, formatted results
        print json.dumps(results, sort_keys=True, indent=2)

if __name__ == '__main__':
    main()

#https://maps.googleapis.com/maps/api/place/search/json?sensor=false&radius=500&location=40.699663%2C-73.992178&key=AIzaSyAxgU3LPU-m5PI7Jh7YTYYKAz6lV6bz2ok&name=Seasons+-+Brooklyn+Heights

#http://maps.google.com/maps/place?hl=en&um=1&ie=UTF-8&q=The+Mill+at+Spring+Lake+Heights&fb=1&gl=us&hq=The+Mill+at&hnear=0x89c187e1ee4821e7:0x92e285115482d250,Spring+Lake+Heights,+NJ&cid=14318798486997774868&ei=uzb6TZ3rGcbZgAeCpaWbBQ&sa=X&oi=local_result&ct=placepage-link&resnum=1&ved=0CCYQ4gkwAA

#The Mill at Spring Lake Heights

