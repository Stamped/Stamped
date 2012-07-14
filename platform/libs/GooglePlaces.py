#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import json, logs, string, urllib, urllib2

from optparse       import OptionParser
from libs.Geocoder       import Geocoder
from libs.AKeyBasedAPI   import AKeyBasedAPI
from api.Schemas    import PlaceEntity, Coordinates
from libs.LRUCache       import lru_cache
from libs.CachedFunction import *
from libs.CountedFunction import countedFn

class GooglePlaces(AKeyBasedAPI):
    BASE_URL        = 'https://maps.googleapis.com/maps/api/place'
    FORMAT          = 'json'
    DEFAULT_RADIUS  = 500 # meters
    NAME            = 'GooglePlaces'
    TYPES           = set([ 'restaurant' ])
    
    API_KEYS = [
        'AIzaSyAxgU3LPU-m5PI7Jh7YTYYKAz6lV6bz2ok',  # Travis
        #'AIzaSyAEjlMEfxmlCBQeyw_82jjobQAFjYx-Las',  # Kevin
        #'AIzaSyDTW6GnCmfP_mdxklSaArWrPoQo6cJQhOs',  # Bart
        #'AIzaSyA90G9YbjX7q3kXOBdmi0JFB3mTCOl45c4',  # Ed
        #'AIzaSyCZnt6jjlHxzRsyklNoYJKsv6kcPeQs-W8',  # Jake
    ]
    
    _googleTypeToSubcategoryMap = {
        "food" : "restaurant", 
        "restaurant" : "restaurant", 
        "grocery_or_supermarket" : "market", 
    }
    
    google_subcategory_whitelist = set([
        "amusement_park", 
        "aquarium", 
        "art_gallery", 
        "bakery", 
        "bar", 
        "beauty_salon", 
        "book_store", 
        "bowling_alley", 
        "cafe", 
        "campground", 
        "casino", 
        "clothing_store", 
        "department_store", 
        "florist", 
        "food", 
        "grocery_or_supermarket", 
        "market", 
        "gym", 
        "home_goods_store", 
        "jewelry_store", 
        "library", 
        "liquor_store", 
        "lodging", 
        "movie_theater", 
        "museum", 
        "night_club", 
        "park", 
        "restaurant", 
        "school", 
        "shoe_store", 
        "shopping_mall", 
        "spa", 
        "stadium", 
        "store", 
        "university", 
        "zoo", 
        "other", 
        "establishment", 
    ])
    
    def __init__(self):
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
    
    def getEntityResultsByLatLng(self, latLng, params=None, detailed=False):
        results = self.getSearchResultsByLatLng(latLng, params)
        output  = []
        
        if results is None:
            return None
        
        for result in results:
            entity = self.getEntityFromResult(result, detailed=detailed)
            
            if entity is not None:
                output.append(entity)
        
        return output
    
    def getEntityFromResult(self, result, detailed=False):
        if result is None:
            return None
        
        entity = self.parseEntity(result)
        
        if entity is None:
            return None
        
        if detailed:
            # fetch a google places details request to fill in any missing data
            details = self.getPlaceDetails(result['reference'])
            
            self.parseEntityDetail(details, entity)
        
        return entity
    
    def parseEntity(self, result, valid=False):
        subcategory  = self.getSubcategoryFromTypes(result['types'])
        if not valid and subcategory not in self.google_subcategory_whitelist:
            return None
        
        entity                                  = PlaceEntity()
        entity.title                            = result['name']
        coordinates                             = Coordinates()
        coordinates.lat                         = result['geometry']['location']['lat']
        coordinates.lng                         = result['geometry']['location']['lng']
        entity.coordinates                      = coordinates
        entity.sources.googleplaces_id          = result['id']
        entity.sources.googleplaces_reference   = result['reference']
        
        # TODO: TYPE
        types = set(entity.types)
        types.add(subcategory)
        entity.types = list(types)
        
        """
        if result['icon'] != u'http://maps.gstatic.com/mapfiles/place_api/icons/restaurant-71.png' and \
           result['icon'] != u'http://maps.gstatic.com/mapfiles/place_api/icons/generic_business-71.png':
            entity.image = result['icon']
        """
        
        if 'vicinity' in result:
            entity.neighborhood = result['vicinity']
        
        return entity
    
    def parseEntityDetail(self, result, entity):
        if result is not None:
            if 'formatted_phone_number' in result:
                entity.phone = result['formatted_phone_number']
            if 'formatted_address' in result:
                entity.address = result['formatted_address']
            if 'address_components' in result:
                entity.address_components = result['address_components']
        
        return entity

    # note: these decorators add tiered caching to this function, such that
    # results will be cached locally with a very small LRU cache of 64 items
    # and also cached remotely via memcached with a TTL of 7 days
    @countedFn(name='GooglePlaces (before caching)')
    @lru_cache(maxsize=64)
    @cachedFn()
    @countedFn(name='GooglePlaces (after caching)')
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
                utils.log('[GooglePlaces] error searching "' + str(latLng) + '"\n' + 
                          'ErrorCode: ' + str(response['status']) + '\n')

                import pprint
                pprint.pprint(response)
                
                if response['status'] == 'OVER_QUERY_LIMIT':
                    count += 1
                    continue
                else:
                    return None
            
            return response['results']

    # note: these decorators add tiered caching to this function, such that
    # results will be cached locally with a very small LRU cache of 64 items
    # and also cached remotely via memcached with a TTL of 7 days
    @countedFn(name='GooglePlaces (before caching)')
    @lru_cache(maxsize=64)
    @cachedFn()
    @countedFn(name='GooglePlaces (after caching)')
    def getAutocompleteResults(self, latLng, query, params=None):
        (offset, count) = self._initAPIKeyIndices()
        
        while True:
            # try a different API key for each attempt
            apiKey = self._getAPIKey(offset, count)
            if apiKey is None:
                return None
            print apiKey
            response = self._getAutocompleteResponse(latLng, query, apiKey, params)

            if response is None:
                return None
            
            #utils.log(json.dumps(response, sort_keys=True, indent=2))
            
            # ensure that we received a valid response
            if response['status'] != 'OK' or len(response['predictions']) <= 0:
                utils.log('[GooglePlaces] error autocompleting "%s" (ErrorCode: %s)\n' %
                          (query, response['status']))

                if response['status'] == 'OVER_QUERY_LIMIT':
                    count += 1
                    continue
                else:
                    return None
            
            return response['predictions']
    
    def getEntityAutocompleteResults(self, query, latLng=None, params=None):
        results = self.getAutocompleteResults(latLng, query, params)
        output  = []
        
        if results is not None:
            for result in results:
                entity = PlaceEntity()
                
                entity.sources.googleplaces_id        = result['id']
                entity.sources.googleplaces_reference = result['reference']
                
                try:
                    terms = result['terms']
                    entity.title = terms[0]['value']
                    
                    if len(terms) > 1:
                        if terms[-1]['value'] == "United States":
                            terms = terms[:-1]
                        
                        entity.formatted_address = string.joinfields((v['value'] for v in terms[1:]), ', ')
                except:
                    entity.title = result['description']
                
                output.append(entity)
        
        return output
    
    def _getSearchResponseByLatLng(self, latLng, apiKey, optionalParams=None):
        params = {
            'location' : self._geocoder.getEncodedLatLng(latLng), 
            'radius'   : self.DEFAULT_RADIUS, 
            'sensor'   : 'false', 
            'key'      : apiKey, 
        }
        
        self._handleParams(params, optionalParams)
        
        # example URL:
        # https://maps.googleapis.com/maps/api/place/search/json?location=-33.8670522,151.1957362&radius=500&types=food&name=harbour&sensor=false&key=AIzaSyAxgU3LPU-m5PI7Jh7YTYYKAz6lV6bz2ok
        url = self._getAPIURL('search', params)
        utils.log('[GooglePlaces] ' + url)
        
        try:
            # GET the data and parse the response as json
            return json.loads(utils.getFile(url))
        except:
            utils.log('[GooglePlaces] unexpected error searching "' + url + '"')
            return None
        
        return None

    # note: these decorators add tiered caching to this function, such that
    # results will be cached locally with a very small LRU cache of 64 items
    # and also cached remotely via memcached with a TTL of 7 days
    @countedFn(name='GooglePlaces (before caching)')
    @lru_cache(maxsize=64)
    @cachedFn()
    @countedFn(name='GooglePlaces (after caching)')
    def getPlaceDetailsResponse(self, reference, apiKey, optionalParams=None):
        params = {
            'reference' : reference, 
            'sensor'    : 'false', 
            'key'       : apiKey, 
        }
        
        self._handleParams(params, optionalParams)
        
        # example URL:
        # https://maps.googleapis.com/maps/api/place/details/json?reference=...&sensor=false&key=AIzaSyAxgU3LPU-m5PI7Jh7YTYYKAz6lV6bz2ok
        url = self._getAPIURL('details', params)
        utils.log('[GooglePlaces] ' + url)
        
        try:
            # GET the data and parse the response as json
            return json.loads(utils.getFile(url))
        except:
            utils.log('[GooglePlaces] unexpected error searching "' + url + '"')
        
        return None

    def addPlaceReport(self, entity):
        params = {
            'sensor' : 'false', 
            'key'    : self._getAPIKey(0, 0), 
        }
        
        post_params = {
            'location' : {
                'lat' : entity.lat, 
                'lng' : entity.lng, 
            }, 
            'name' : entity.title, 
            'accuracy' : 50, 
            'types' : [ ], 
            'language' : 'en-US', 
        }
        
        url = self._getAPIURL('add', params)
        #utils.log(url)
        
        try:
            data = json.dumps(post_params)
            request = urllib2.Request(url, data, {'Content-Type': 'application/json'})
            request = urllib2.urlopen(request)
            response = request.read()
            return response
        except:
            return None
    
    def _getAutocompleteResponse(self, latLng, query, apiKey, optionalParams=None):
        params = {
            'input'  : query, 
            'sensor' : 'false', 
            'types'  : 'establishment', 
            'key'    : apiKey, 
        }
        
        if latLng is not None:
            params['location'] = self._geocoder.getEncodedLatLng(latLng)

        self._handleParams(params, optionalParams)
        
        # example URL:
        # https://maps.googleapis.com/maps/api/place/autocomplete/json?input=test&sensor=false&key=AIzaSyAxgU3LPU-m5PI7Jh7YTYYKAz6lV6bz2ok
        url = self._getAPIURL('autocomplete', params)
        utils.log('[GooglePlaces] ' + url)
        
        try:
            # GET the data and parse the response as json
            return json.loads(utils.getFile(url))
        except:
            utils.log('[GooglePlaces] unexpected error searching "' + url + '"')
            return None
        
        return None
    
    def _handleParams(self, params, optionalParams):
        if optionalParams is not None:
            for key in optionalParams:
                params[key] = optionalParams[key]
        
        for k in params:
            v = params[k]
            if isinstance(v, unicode):
                params[k] = v.encode('utf-8')
    
    def addressToLatLng(self, address):
        latLng = self._geocoder.addressToLatLng(address)
        
        if latLng is None or latLng[0] is None or latLng[1] is None:
            # geocoding translation from address to lat/lng failed
            return None
        
        return latLng
    
    def _getAPIURL(self, method, params):
        return "%s/%s/%s?%s" % (self.BASE_URL, method, self.FORMAT, urllib.urlencode(params))
    
    def getSubcategoryFromTypes(self, types):
        establishment = False
        
        for t in types:
            if t == "establishment":
                establishment = True
            else:
                try:
                    return self._googleTypeToSubcategoryMap[t]
                except KeyError:
                    return t
        
        if establishment:
            return "establishment"
        else:
            return "other"

__globalGooglePlaces = None

def globalGooglePlaces():
    global __globalGooglePlaces

    if __globalGooglePlaces is None:
        __globalGooglePlaces = GooglePlaces()

    return __globalGooglePlaces


def parseCommandLine():
    usage   = "Usage: %prog [options]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)

    parser.add_option("--method", action="store", dest="method", default="search")
    parser.add_option("--address", action="store", dest="address", default=None)
    parser.add_option("--latlng", action="store", dest="latlng", default=None)
    parser.add_option("-q", "--query", action="store", dest="query", default=None)

    defaultRadius = 500
    parser.add_option("-r", "--radius", action="store", type="int", dest="radius", default=defaultRadius,
        help="Optionally specify a radius in meters (defaults to %d meters)" % defaultRadius)
    
    parser.add_option("-t", "--types", action="store", type="string", dest="types",
        default=None, help="Optionally specify one or more types to search by, with " + 
        "each type separated by a pipe symbol (e.g., -t 'food|restaurant'). " + 
        "Note that types must be surrounded by single quotes to prevent shell interpretation " + 
        "of the pipe character(s).")
    
    parser.add_option("-l", "--limit", action="store", type="int", dest="limit",
        default=None, help="Limit the number of results shown to the top n results")
    
    parser.add_option("-v", "--verbose", action="store_true", default=False,
                      help="Print out verbose results")

    parser.set_defaults(types=None)
    parser.set_defaults(limit=None)
    parser.set_defaults(radius=None)
    
    (options, args) = parser.parse_args()

    if options.method not in ['search', 'autocomplete']:
        raise Exception('Unrecognized method: (%s)' % options.method)

    if options.method == 'search' and not options.address and not options.latlng:
        raise Exception('With --method=search, one of --address, --latlng is required!')

    if options.method == 'autocomplete' and not options.query:
        raise Exception('With --method=autocomplete, the --query flag is also required!')

    if options.method == 'autocomplete' and options.address:
        raise Exception('--address is not currently supported with --method=autocomplete!')

    if options.address and options.latlng:
        raise Exception('--address and --latlng flags are mutually exclusive!')

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
    params  = {}

    
    if options.radius:
        params['radius'] = options.radius
    if options.types:
        params['types'] = options.types

    if options.method == 'search':
        if options.query:
            params['name'] = options.query
        if options.address:
            results = places.getSearchResultsByAddress(options.address, params)
        elif options.latlng:
            latlng = options.latlng.split(',')
            results = places.getSearchResultsByLatLng(latlng, params)
    elif options.method == 'autocomplete':
        latlng = options.latlng.split(',')
        results = places.getAutocompleteResults(latlng, options.query, params)

    import pprint
    if results is None:
        print "Failed to return results!"
    else:
        pprint.pprint(results)

    # print the prettified, formatted results
    # print json.dumps(results, sort_keys=True, indent=2)

if __name__ == '__main__':
    main()

