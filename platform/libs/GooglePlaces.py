#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import json, logs, string, urllib, urllib2

from optparse       import OptionParser
from Geocoder       import Geocoder
from AKeyBasedAPI   import AKeyBasedAPI
from AEntitySource  import AExternalServiceEntitySource
from api.Schemas    import PlaceEntity
from LRUCache       import lru_cache
from Memcache       import memcached_function

class GooglePlaces(AExternalServiceEntitySource, AKeyBasedAPI):
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
        
        entity = PlaceEntity()
        entity.title = result['name']
        entity.lat   = result['geometry']['location']['lat']
        entity.lng   = result['geometry']['location']['lng']
        entity.googleplaces_id          = result['id']
        entity.googleplaces_reference   = result['reference']
        
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
                          'ErrorCode: ' + response['status'] + '\n')
                
                if response['status'] == 'OVER_QUERY_LIMIT':
                    count += 1
                    continue
                else:
                    return None
            
            return response['results']
    
    def getAutocompleteResults(self, latLng, query, params=None):
        (offset, count) = self._initAPIKeyIndices()
        
        while True:
            # try a different API key for each attempt
            apiKey = self._getAPIKey(offset, count)
            if apiKey is None:
                return None
            
            response = self._getAutocompleteResponse(latLng, query, apiKey, params)
            
            if response is None:
                return None
            
            #utils.log(json.dumps(response, sort_keys=True, indent=2))
            
            # ensure that we received a valid response
            if response['status'] != 'OK' or len(response['predictions']) <= 0:
                utils.log('[GooglePlaces] error autocompleting "' + query + '"\n' + 
                          'ErrorCode: ' + response['status'] + '\n')
                
                if response['status'] == 'OVER_QUERY_LIMIT':
                    count += 1
                    continue
                else:
                    return None
            
            return response['predictions']
    
    # note: these decorators add tiered caching to this function, such that 
    # results will be cached locally with a very small LRU cache of 64 items 
    # and also cached remotely via memcached with a TTL of 7 days
    @lru_cache(maxsize=64)
    @memcached_function(time=7*24*60*60)
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
        
        if optionalParams is not None:
            for key in optionalParams:
                params[key] = optionalParams[key]
        
        for k in params:
            v = params[k]
            
            if isinstance(v, unicode):
                params[k] = v.encode("ascii", "xmlcharrefreplace")
        
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
                params[k] = v.encode("ascii", "xmlcharrefreplace")
    
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
    
    d = 500
    parser.add_option("-r", "--radius", action="store", type="int", dest="radius", 
        default=d, help="Optionally specify a radius in meters (defaults to %d meters)" % d)
    
    parser.add_option("-t", "--types", action="store", type="string", dest="types", 
        default=None, help="Optionally specify one or more types to search by, with " + 
        "each type separated by a pipe symbol (e.g., -t 'food|restaurant'). " + 
        "Note that types must be surrounded by single quotes to prevent shell interpretation " + 
        "of the pipe character(s).")
    
    parser.add_option("-l", "--limit", action="store", type="int", dest="limit", 
        default=None, help="Limit the number of results shown to the top n results")
    
    parser.add_option("-v", "--verbose", action="store_true", default=False, 
                      help="Print out verbose results")
    
    parser.add_option("-s", "--suggest", action="store_true", default=False, 
                      help="Use Places autosuggest API")
    
    parser.add_option("-d", "--detail", action="store_true", default=False, 
                      help="Use Places detail API")
    
    parser.set_defaults(address=True)
    parser.set_defaults(name=None)
    parser.set_defaults(types=None)
    parser.set_defaults(limit=None)
    parser.set_defaults(radius=None)
    
    (options, args) = parser.parse_args()
    
    if len(args) < 1:
        parser.print_help()
        return None
    
    if not options.suggest and options.radius is None:
        options.radius = 500
    
    do = True
    if options.suggest or options.detail:
        if len(args) > 1:
            options.input = args[1]
            args[0] = args[1]
        else:
            options.input = args[0]
            do = False
    
    if do and not options.address:
        lat, lng = args[0].split(',')
        lat, lng = float(lat), float(lng)
        args[0] = (lat, lng)
    
    options.latLng = args[0]
    
    return (options, args)


from LRUCache import lru_cache
@lru_cache(3)
def test_lrucache(arbitrary_arg, copies):
    suggested = []

    def _add_suggested_section(title, entities):
        suggested.append({ 'name' : title, 'entities' : entities })
    import random
    import copy

    random.seed()

    entity = PlaceEntity()
    entity.title = 'Test'
    entity.lat   = float(random.randint(0,100000))
    entity.lng   = float(random.randint(0,100000))
    entity.googleplaces_id          = 'theGooglePlacesId'
    entity.googleplaces_reference   = 'theGooglePlacesReference'

    entities = []
    for x in xrange(copies):
        entities.append(copy.copy(entity))

    _add_suggested_section('testEntities', entities )

    return suggested



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
    
    if options.name:
        params['name'] = options.name
    if options.radius:
        params['radius'] = options.radius
    if options.types:
        params['types'] = options.types
    
    if options.detail:
        results = places.getPlaceDetails(options.input, params)
    elif options.suggest:
        results = places.getAutocompleteResults(options.latLng, options.input, params)
    elif options.address:
        results = places.getSearchResultsByAddress(options.latLng, params)
    else:
        results = places.getSearchResultsByLatLng(options.latLng, params)
    
    if results is None:
        print "Failed to return results for '%s'" % (options.latLng, )
    else:
        if options.limit:
            results = results[0:min(options.limit, len(results))]
        
        # print the prettified, formatted results
        print json.dumps(results, sort_keys=True, indent=2)

"""
g=GooglePlaces()
from Schemas import Entity
e=Entity()
e.title = 'TEST_PLACE_DELETE'
e.lat = 43.0
e.lng = -71
r = g.addPlaceReport(e)
print r
"""

"""
p = GooglePlaces()
#f = "CkQ6AAAAe9fbCd2v01fWvsL1pth68lnlyo2zugxpxZZV8-qBHRyA6q5_YkHpeETA8Vt5KpNkGAzDQUIkXUT3RKG3EFPPyBIQpMwl-TJnQi3amCWI9_r6YBoUzs7f38upa92ztqtXe5EDaSudw2Q"
f = "CmRaAAAAyyIyNPbq2JCfERw_8mVh6CKEujLmheDtYSAGEd6ZF4PmnPg2_s7vw5MlBlx49ohoSp6JIM0xhcNlQXvR30G2kSk5NRE4u1317ALVY4FDZBdrrFkf-yx86hvFYgRz5D3_EhDgTQ-fyzUyNnNHd7UhpRIEGhQ1e2xcP4vhqxD4kozQXHVmde4pXA"
r = p.getPlaceDetails(f)
from pprint import pprint
pprint(r)
"""

if __name__ == '__main__':
    main()

