#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import json, logs, urllib

from optparse import OptionParser
from Geocoder import Geocoder
from AKeyBasedAPI import AKeyBasedAPI
from AEntitySource import AExternalServiceEntitySource
from Schemas import Entity

class GooglePlaces(AExternalServiceEntitySource, AKeyBasedAPI):
    BASE_URL        = 'https://maps.googleapis.com/maps/api/place'
    FORMAT          = 'json'
    DEFAULT_RADIUS  = 500 # meters
    NAME            = 'GooglePlaces'
    TYPES           = set([ 'restaurant' ])
    
    API_KEYS = [
        'AIzaSyAxgU3LPU-m5PI7Jh7YTYYKAz6lV6bz2ok',  # Travis
        'AIzaSyAEjlMEfxmlCBQeyw_82jjobQAFjYx-Las',  # Kevin
        'AIzaSyDTW6GnCmfP_mdxklSaArWrPoQo6cJQhOs',  # Bart
        'AIzaSyA90G9YbjX7q3kXOBdmi0JFB3mTCOl45c4',  # Ed
        'AIzaSyCZnt6jjlHxzRsyklNoYJKsv6kcPeQs-W8',  # Jake
    ]
    
    _googleTypeToSubcategoryMap = {
        "food" : "restaurant", 
        "restaurant" : "restaurant", 
        "grocery_or_supermarket" : "market", 
    }
    
    def __init__(self):
        AExternalServiceEntitySource.__init__(self, self.NAME, self.TYPES)
        AKeyBasedAPI.__init__(self, self.API_KEYS)
        
        self._geocoder = Geocoder()
    
    def _run(self):
        pass
    
    def getPlaceDetails(self, reference, params=None):
        (offset, count) = self._initAPIKeyIndices()
        
        while True:
            # try a different API key for each attempt
            apiKey = self._getAPIKey(offset, count)
            if apiKey is None:
                return None
            
            response = self.getPlaceDetailsResponse(reference, apiKey, params)
            
            if response is None:
                return None
            
            # ensure that we received a valid response
            if response['status'] != 'OK':
                #utils.log('[GooglePlaces] error searching "' + reference + '"\n' + 
                #          'ErrorCode: ' + response['status'] + '\n')
                
                if response['status'] == 'OVER_QUERY_LIMIT':
                    count += 1
                    continue
                else:
                    return None
            
            return response['result']
    
    def getSearchResultsByAddress(self, address, params=None):
        latLng = self.addressToLatLng(address)
        
        if latLng is None:
            # geocoding translation from address to lat/lng failed, so we will 
            # be unable to cross-reference this address with google places.
            return None
        
        return self.getSearchResultsByLatLng(latLng, params)
    
    def getEntityResultsByLatLng(self, latLng, params=None):
        results = self.getSearchResultsByLatLng(latLng, params)
        output  = []
        
        for result in results:
            entity = Entity()
            entity.title = result['name']
            entity.image = result['icon']
            entity.lat   = result['geometry']['location']['lat']
            entity.lng   = result['geometry']['location']['lng']
            entity.gid   = result['id']
            entity.reference = result['reference']
            entity.neighborhood = result['vicinity']
            
            output.append(entity)
        
        return output
    
    def getSearchResultsByLatLng(self, latLng, params=None):
        (offset, count) = self._initAPIKeyIndices()
        
        while True:
            # try a different API key for each attempt
            apiKey = self._getAPIKey(offset, count)
            if apiKey is None:
                return None
            
            response = self._getSearchResponseByLatLng(latLng, apiKey, params)
            
            if response is None:
                return None
            
            #utils.log(json.dumps(response, sort_keys=True, indent=2))
            
            # ensure that we received a valid response
            if response['status'] != 'OK' or len(response['results']) <= 0:
                #utils.log('[GooglePlaces] error searching "' + str(latLng) + '"\n' + 
                #          'ErrorCode: ' + response['status'] + '\n')
                
                if response['status'] == 'OVER_QUERY_LIMIT':
                    count += 1
                    continue
                else:
                    return None
            
            return response['results']
    
    def _getSearchResponseByLatLng(self, latLng, apiKey, optionalParams=None):
        params = {
            'location' : self._geocoder.getEncodedLatLng(latLng), 
            'radius'   : self.DEFAULT_RADIUS, 
            'sensor'   : 'false', 
            'key'      : apiKey, 
        }
        
        if optionalParams is not None:
            for key in optionalParams:
                params[key] = optionalParams[key]
        
        # example URL:
        # https://maps.googleapis.com/maps/api/place/search/json?location=-33.8670522,151.1957362&radius=500&types=food&name=harbour&sensor=false&key=AIzaSyAxgU3LPU-m5PI7Jh7YTYYKAz6lV6bz2ok
        url = self._getAPIURL('search', params)
        #logs.debug('[GooglePlaces] ' + url)
        
        try:
            # GET the data and parse the response as json
            return json.loads(utils.getFile(url))
        except:
            utils.log('[GooglePlaces] unexpected error searching "' + url + '"')
            return None
        
        return None
    
    def getPlaceDetailsResponse(self, reference, apiKey, optionalParams=None):
        params = {
            'reference' : reference, 
            'sensor'    : 'false', 
            'key'       : apiKey, 
        }
        
        if optionalParams is not None:
            for key in optionalParams:
                params[key] = optionalParams[key]
        
        # example URL:
        # https://maps.googleapis.com/maps/api/place/details/json?reference=...&sensor=false&key=AIzaSyAxgU3LPU-m5PI7Jh7YTYYKAz6lV6bz2ok
        url = self._getAPIURL('details', params)
        #logs.debug('[GooglePlaces] ' + url)
        
        try:
            # GET the data and parse the response as json
            return json.loads(utils.getFile(url))
        except:
            utils.log('[GooglePlaces] unexpected error searching "' + url + '"')
        
        return None
    
    def addressToLatLng(self, address):
        latLng = self._geocoder.addressToLatLng(address)
        
        if latLng is None or latLng[0] is None or latLng[1] is None:
            # geocoding translation from address to lat/lng failed
            return None
        
        return latLng
    
    def _getAPIURL(self, method, params):
        return self.BASE_URL + '/' + method + '/' + self.FORMAT + '?' + urllib.urlencode(params)
    
    def getSubcategoryFromTypes(self, types):
        for t in types:
            if t != "establishment":
                try:
                    return self._googleTypeToSubcategoryMap[t]
                except KeyError:
                    return t
        
        return "other"

def parseCommandLine():
    usage   = "Usage: %prog [options] address|latLng"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-a", "--address", action="store_true", dest="address", 
        default=True, help="Parse the argument as an address")
    parser.add_option("-b", "--latLng", action="store_false", dest="address", 
        default=False, help="Parse the argument as an encoded latitude/longitude pair (e.g., '40.144729,-74.053527')")
    parser.add_option("-n", "--name", action="store", type="string", dest="name", 
        default=None, help="Optionally provide a name to filter results")
    parser.add_option("-r", "--radius", action="store", type="int", dest="radius", 
        default=500, help="Optionally specify a radius in meters (defaults to %default meters)")
    parser.add_option("-t", "--types", action="store", type="string", dest="types", 
        default=None, help="Optionally specify one or more types to search by, with " + 
        "each type separated by a pipe symbol (e.g., -t 'food|restaurant'). " + 
        "Note that types must be surrounded by single quotes to prevent shell interpretation " + 
        "of the pipe character(s).")
    parser.add_option("-l", "--limit", action="store", type="int", dest="limit", 
        default=None, help="Limit the number of results shown to the top n results")
    #parser.add_option("-d", "--detail", action="store_true", dest="detail", 
    #    default=False, help="Included more detailed search result info.")
    
    parser.set_defaults(address=True)
    parser.set_defaults(name=None)
    parser.set_defaults(types=None)
    parser.set_defaults(limit=None)
    parser.set_defaults(radius=500)
    parser.set_defaults(detail=False)
    
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.print_help()
        return None
    
    if not options.address:
        lat, lng = args[0].split(',')
        lat, lng = float(lat), float(lng)
        args[0] = (lat, lng)
    
    return (options, args)

def main():
    """
        Usage: GooglePlaces.py [options] address|latLng

        Options:
          --version             show program's version number and exit
          -h, --help            show this help message and exit
          -a, --address         Parse the argument as an address
          -b, --latLng          Parse the argument as an encoded latitude/longitude
                                pair (e.g., '40.144729,-74.053527')
          -n NAME, --name=NAME  Optionally provide a name to filter results
          -r RADIUS, --radius=RADIUS
                                Optionally specify a radius in meters (defaults to 500
                                meters)
          -t TYPES, --types=TYPES
                                Optionally specify one or more types to search by,
                                with each type separated by a pipe symbol (e.g., -t
                                'food|restaurant'). Note that types must be surrounded
                                by single quotes to prevent shell interpretation of
                                the pipe character(s).
          -l LIMIT, --limit=LIMIT
                                Limit the number of results shown to the top n results
    """
    
    result = parseCommandLine()
    if result is None:
        return
    
    (options, args) = result
    
    places = GooglePlaces()
    results = []
    optionalParams = {}
    
    if options.name:
        optionalParams['name'] = options.name
    if options.radius:
        optionalParams['radius'] = options.radius
    if options.types:
        optionalParams['types'] = options.types
    
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

