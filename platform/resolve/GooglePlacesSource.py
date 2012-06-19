#!/usr/bin/env python

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
    import logs
    import math
    import string
    from GenericSource              import GenericSource
    from GooglePlaces               import GooglePlaces
    from Resolver                   import *
    from ResolverObject             import *
    from utils                      import lazyProperty
    from gevent.pool                import Pool
    from datetime                   import datetime
    from functools                  import partial
    from LibUtils                   import states
    from pprint                     import pformat
    from search.ScoringUtils        import *
    from difflib                    import SequenceMatcher
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


"""
{u'address_components': [{u'long_name': u'3583',
                          u'short_name': u'3583',
                          u'types': [u'street_number']},
                         {u'long_name': u'16th Street',
                          u'short_name': u'16th Street',
                          u'types': [u'route']},
                         {u'long_name': u'San Francisco',
                          u'short_name': u'San Francisco',
                          u'types': [u'locality', u'political']},
                         {u'long_name': u'CA',
                          u'short_name': u'CA',
                          u'types': [u'administrative_area_level_1',
                                     u'political']},
                         {u'long_name': u'US',
                          u'short_name': u'US',
                          u'types': [u'country', u'political']},
                         {u'long_name': u'94114',
                          u'short_name': u'94114',
                          u'types': [u'postal_code']}],
 u'formatted_address': u'3583 16th Street, San Francisco, CA 94114, United States',
 u'formatted_phone_number': u'(415) 252-7500',
 u'geometry': {u'location': {u'lat': 37.764162, u'lng': -122.432551}},
 u'icon': u'http://maps.gstatic.com/mapfiles/place_api/icons/restaurant-71.png',
 u'id': u'60dc209008ebd294862b36e14861c246f8f04c0f',
 u'international_phone_number': u'+1 415-252-7500',
 u'name': u'Starbelly',
 u'rating': 4.0,
 u'reference': u'CnRhAAAAgr8mDfHDkIni5SGQpNVm3WeJdYSm6HlCD8AmMGj_ONdPq-USOnaFZ_3GYgBx232kQchQS2MF6Dy0NumTJwIBaaLevPv1I3u0OaEFEk6n1jEyKKnmVGwatZ3hv49D5UeY2CG2FR_pghI5gYxxv5JqkRIQ9bFh6GNIxQiIu5suHV5kfxoUxcsiAnn4SjV7BmSpB6Q7SvS3SD0',
 u'types': [u'restaurant', u'food', u'establishment'],
 u'url': u'http://maps.google.com/maps/place?cid=15943452779294078432',
 u'vicinity': u'3583 16th Street, San Francisco',
 u'website': u'http://www.starbellysf.com/'}
"""


class GooglePlacesPlace(ResolverPlace):

    def __init__(self, data):
        # Note: We don't bother with maxLookupCalls with FactualPlaces because right now we know that if data!=None
        # there won't be any lookup calls. If you change the code to implicitly call Factual even when data is provided
        # in the constructor, please add a maxLookupCalls __init__ kwarg and set it to 0 in the constructor calls from
        # GooglePlacesSource.searchLite().
        ResolverPlace.__init__(self)
        self.__data = data

    @lazyProperty
    def key(self):
        try:
            return self.data['reference']
        except Exception:
            return ''

    @lazyProperty
    def data(self):
        return self.__data

    @lazyProperty
    def name(self):
        return self.data['name']

    @lazyProperty
    def coordinates(self):
        try:
            return (self.data['geometry']['location']['lat'], self.data['geometry']['location']['lng'])
        except Exception:
            return None
    
    @lazyProperty
    def address_string(self):
        if 'address_string' in self.data:
            return self.data['address_string']
        elif 'vicinity' in self.data:
            return self.data['vicinity']
        return None

    @lazyProperty
    def address(self):
        if 'address_components' not in self.data:
            return {}
        
        data   = { }
        number = None
        route  = None
        
        for comp in self.data['address_components']:
            if 'types' in comp and 'long_name' in comp:
                name = comp['long_name']
                types = comp['types']
                if 'administrative_area_level_1' in types:
                    #TODO consider country checking
                    if name in states:
                        name = states[name]
                    data['region'] = name
                elif 'country' in types:
                    data['country'] = name
                elif 'postal_code' in types:
                    data['postcode'] = name
                elif 'locality' in types:
                    data['locality'] = name
                elif 'street_number' in types:
                    number = name
                elif 'route' in types:
                    route = name
        
        for comp in self.data['address_components']:
            if 'types' in comp and 'long_name' in comp:
                name = comp['long_name']
                types = comp['types']
                if 'sublocality' in types and 'locality' not in data:
                    data['locality'] = name
        
        if route is not None and number is not None:
            data['street'] = "%s %s" % (number, route)
        
        return data

    @lazyProperty
    def neighborhoods(self):
        locality = None
        sublocality = None
        if 'address_components' in self.data:
            for comp in self.data['address_components']:
                if 'types' in comp and 'long_name' in comp:
                    name = comp['long_name']
                    types = comp['types']
                    if 'locality' in types:
                        locality = name
                    elif 'sublocality' in types:
                        sublocality = name
        
        if locality is not None and sublocality is not None:
            return [sublocality]
        else:
            return []
    
    @lazyProperty
    def phone(self):
        try:
            if 'formatted_phone_number' in self.data:
                return self.data['formatted_phone_number']
        except:
            pass
        return None
    
    @lazyProperty
    def types(self):
        if 'types' in self.data:
            __types = self.data['types']
            if 'food' in self.data['types'] or 'restaurant' in self.data['types']:
                return ['restaurant']
            if 'grocery_or_supermarket' in self.data['types']:
                return ['market']
            if 'establishment' in self.data['types']:
                return ['establishment']
        return []

    @property 
    def source(self):
        return 'googleplaces'
    
    def __repr__(self):
        return pformat(self.data)


class GooglePlacesAutocompletePlace(ResolverPlace):
    """
    Right now GooglePlacesPlace sort of encapsulates GooglePlaces data that came in either through a lookup or a
    search result. They're fairly similar so that's alright for now, but autocomplete places are a lot more restricted
    and the data you're looking for is in different places so they deserve their own class.

    TODO: Split out any common functionality with GooglePlacesPlace to a superclass, possibly also split out the
    lookup/search results into separate classes.
    """
    def __init__(self, data):
        ResolverPlace.__init__(self)
        self.__data = data

    @property
    def source(self):
        return 'googleplaces'

    @property
    def key(self):
        return self.__data['id']

    @lazyProperty
    def __terms(self):
        try:
            return [term['value'] for term in self.__data['terms']]
        except Exception:
            # TODO: Why might this throw an exception?
            return []

    @lazyProperty
    def name(self):
        if self.__terms:
            return self.__terms[0]
        return self.__data['description']

    @property
    def reference(self):
        return self.__data['reference']

    @lazyProperty
    def address_string(self):
        address_components = self.__terms[1:]
        if not address_components:
            return ''
        if address_components[-1] == 'United States':
            del address_components[-1]
        return string.joinfields(address_components, ', ')

    def __repr__(self):
        return pformat(self.data)


class GooglePlacesSearchAll(ResolverProxy, ResolverSearchAll):

    def __init__(self, target):
        ResolverProxy.__init__(self, target)
        ResolverSearchAll.__init__(self)


class GooglePlacesSource(GenericSource):
    """
    Data-Source proxy for Google Places.
    """
    def __init__(self):
        GenericSource.__init__(self, 'googleplaces',
            groups=[
                'address',
                'formatted_address',
                'phone',
                'site',
                'neighborhood',
                'coordinates',
            ],
            kinds=[
                'place',
            ]
        )
    
    @lazyProperty
    def __places(self):
        return GooglePlaces()
    
    def matchSource(self, query):
        if query.type == 'place':
            return self.placeSource(query)
        elif query.type == 'search_all':
            return self.searchAllSource(query)
        
        return self.emptySource
    
    def placeSource(self, query):
        def gen():
            try:
                params = {
                    'radius': 20000,
                    'name': query.name
                }
                gdata = self.__places.getSearchResultsByLatLng(query.coordinates, params)
                if gdata is not None:
                    for gdatum in gdata:
                        if 'reference' in gdatum:
                            ref = gdatum['reference']
                            details = self.__places.getPlaceDetails(ref)
                            details['reference'] = ref
                            yield GooglePlacesPlace(details)
            except GeneratorExit:
                pass
        
        return self.generatorSource(gen())

    def searchAllSource(self, query, timeout=None):
        if query.kinds is not None and len(query.kinds) > 0 and len(self.kinds.intersection(query.kinds)) == 0:
            logs.debug('Skipping %s (kinds: %s)' % (self.sourceName, query.kinds))
            return self.emptySource

        logs.debug('Searching %s...' % self.sourceName)
        
        def gen():
            try:
                raw_results = []
                
                def getGooglePlacesSearch(q):
                    # Hacky conversion
                    params  = {'name': q.query_string, 'radius': 20000}
                    results = self.__places.getEntityResultsByLatLng(q.coordinates, params)
                    
                    if results is None:
                        return self.emptySource
                    
                    for result in results:
                        data = {}
                        data['reference']       = result.sources.googleplaces_reference
                        data['name']            = result.title
                        data['latitude']        = result.coordinates.lat
                        data['longitude']       = result.coordinates.lng
                        data['address_string']  = result.neighborhood
                        data['type']            = result.subcategory
                        
                        raw_results.append(data)
                
                def getGoogleNationalSearch(q):
                    results = self.__places.getEntityAutocompleteResults(q.query_string, q.coordinates)
                    
                    for result in results:
                        # Hacky conversion
                        data = {}
                        data['reference']       = result.sources.googleplaces_reference
                        data['name']            = result.title
                        data['address_string']  = result.formatted_address
                        raw_results.append(data)
                
                if query.coordinates is not None:
                    pool = Pool(2)
                    pool.spawn(getGooglePlacesSearch, query)
                    pool.spawn(getGoogleNationalSearch, query)
                    pool.join(timeout=timeout)
                else:
                    getGoogleNationalSearch(query)
                
                for result in raw_results:
                    yield GooglePlacesSearchAll(GooglePlacesPlace(result))
            except GeneratorExit:
                pass
        
        return self.generatorSource(gen())

    def searchLite(self, queryCategory, queryText, timeout=None, queryLatLng=None):
        if (queryCategory != 'place'):
            raise NotImplementedError()

        print "queryText is", queryText
        print "queryCategory is", queryCategory
        print "queryLatLng is", queryLatLng

        localResults = []
        nationalResults = []
        def searchLocally():
            results = self.__places.getSearchResultsByLatLng(queryLatLng, params={'name': queryText, 'radius': 20000})
            if results:
                localResults.extend(results)
        def searchNationally():
            results = self.__places.getAutocompleteResults(queryLatLng, queryText)
            if results:
                nationalResults.extend(results)
        if queryLatLng:
            pool = Pool(2)
            pool.spawn(searchLocally)
            pool.spawn(searchNationally)
            pool.join(timeout=timeout)
        else:
            searchNationally()

        # Convert JSON objects to GooglePlacesPages.
        localResults = [GooglePlacesPlace(result) for result in localResults]
        nationalResults = [GooglePlacesAutocompletePlace(result) for result in nationalResults]

        # Start with super basic scoring. Score local results significantly lower because they can get boosts for
        # title and proximity, but national results only ever get title boosts because we don't have lat-lngs.
        # TODO: Investigate adding in city name querytext matching to the score augmentation!
        localResults = scoreResultsWithBasicDropoffScoring(localResults, sourceScore=0.4, dropoffFactor=0.9)
        nationalResults = scoreResultsWithBasicDropoffScoring(nationalResults, sourceScore=0.6, dropoffFactor=0.9)

        augmentPlaceScoresForRelevanceAndProximity(localResults, queryText, queryLatLng)
        augmentPlaceScoresForRelevanceAndProximity(nationalResults, queryText, queryLatLng)

        smoothScores(localResults)
        smoothScores(nationalResults)

        return dedupeById(localResults + nationalResults)


    def entityProxyFromKey(self, key, **kwargs):
        try:
            item = self.__places.getPlaceDetails(key)
            return GooglePlacesPlace(item)
        except KeyError:
            pass
        
        return None
    
    def enrichEntity(self, entity, controller, decorations, timestamps):
        if not controller.shouldEnrich('googleplaces', self.sourceName, entity):
            return False
        
        details = self.__details(entity)
        if details is None:
            entity.sources.googleplaces_id = None
            timestamps['googleplaces'] = controller.now
            return True
        else:
            entity.sources.googleplaces_reference = details['reference']
        
        reformatted = self.__reformatAddress(details)
        if reformatted is not None:
            self.writeFields(entity, None, reformatted)
        
        neighborhood = self.__neighborhood(details)
        if neighborhood is not None:
            entity.neighborhood = neighborhood
        
        if 'formatted_phone_number' in details and details['formatted_phone_number'] != '':
            entity.phone = details['formatted_phone_number']
        
        if 'website' in details and details['website'] != '':
            entity.site = details['website']
        
        return True

    def enrichEntityWithEntityProxy(self, proxy, entity, controller=None, decorations=None, timestamps=None):
        GenericSource.enrichEntityWithEntityProxy(self, proxy, entity, controller, decorations, timestamps)
        entity.sources.googleplaces_id = proxy.key
        entity.sources.googleplaces_reference = proxy.key
        ### NOTE: It looks like the proxy.key is actually the reference. Shouldn't this be the id?
        return True
    
    def __details(self, entity):
        try:
            details = None
            if 'coordinates' in entity and 'title' in entity:
                gdata = self.__places.getSearchResultsByLatLng((entity.coordinates.lat, entity.coordinates.lng),{'name':entity.title})
                if gdata is not None and len(gdata) > 0:
                    gdatum = gdata[0]
                    if 'reference' in gdatum:
                        ref = gdatum['reference']
                        details = self.__places.getPlaceDetails(ref)
                        details['reference'] = ref
            return details
        except:
            return None
    
    def __neighborhood(self, details):
        locality    = None
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
        route  = None
        
        for comp in results['address_components']:
            if 'types' in comp and 'long_name' in comp:
                name  = comp['long_name']
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
                
                if 'sublocality' in types and data['address_locality'] is None:
                    data['address_locality'] = name
        
        if route is not None and number is not None:
            data['address_street'] = "%s %s" % (number, route)
        
        data2 = {}
        for k,v in data.items():
            if v is None and k != 'address_street_ext':
                return None
            
            data2[tuple(k.split('.'))] = _constant(v)
        
        return data2
    
if __name__ == '__main__':
    demo(GooglePlacesSource(), 'Barley Swine')

