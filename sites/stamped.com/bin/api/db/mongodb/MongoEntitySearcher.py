#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import logs, math, pymongo, re, string
import CityList

from EntitySearcher import EntitySearcher
from GooglePlaces   import GooglePlaces
from libs.AmazonAPI import AmazonAPI
from Schemas        import Entity
from difflib        import SequenceMatcher
from pymongo.son    import SON
from gevent.pool    import Pool
from pprint         import pprint, pformat
from utils          import lazyProperty

class MongoEntitySearcher(EntitySearcher):
    subcategory_weights = {
        # --------------------------
        #           food
        # --------------------------
        'restaurant'        : 100, 
        'bar'               : 90, 
        'bakery'            : 70, 
        'cafe'              : 70, 
        'market'            : 60, 
        'food'              : 70, 
        'night_club'        : 75, 
        
        # --------------------------
        #           book
        # --------------------------
        'book'              : 50, 
        
        # --------------------------
        #           film
        # --------------------------
        'movie'             : 65, 
        'tv'                : 65, 
        
        # --------------------------
        #           music
        # --------------------------
        'artist'            : 55, 
        'song'              : 20, 
        'album'             : 25, 
        
        # --------------------------
        #           other
        # --------------------------
        'app'               : 15, 
        'other'             : 5, 
        
        # the following subcategories are from google places
        'amusement_park'    : 25, 
        'aquarium'          : 25, 
        'art_gallery'       : 25, 
        'beauty_salon'      : 15, 
        'book_store'        : 15, 
        'bowling_alley'     : 25, 
        'campground'        : 20, 
        'casino'            : 25, 
        'clothing_store'    : 20, 
        'department_store'  : 20, 
        'florist'           : 15, 
        'gym'               : 10, 
        'home_goods_store'  : 5, 
        'jewelry_store'     : 15, 
        'library'           : 5, 
        'liquor_store'      : 10, 
        'lodging'           : 45, 
        'movie_theater'     : 45, 
        'museum'            : 70, 
        'park'              : 50, 
        'school'            : 25, 
        'shoe_store'        : 20, 
        'shopping_mall'     : 20, 
        'spa'               : 25, 
        'stadium'           : 25, 
        'store'             : 15, 
        'university'        : 65, 
        'zoo'               : 65, 
        
        # the following subcategories are from amazon
        'video_game'        : 65
    }
    
    source_weights = {
        'googlePlaces'      : 50, 
        'amazon'            : 90, 
        'openTable'         : 110, 
        'factual'           : 5, 
        'apple'             : 75, 
        'zagat'             : 95, 
        'urbanspoon'        : 80, 
        'nymag'             : 95, 
        'sfmag'             : 95, 
        'latimes'           : 80, 
        'bostonmag'         : 90, 
        'fandango'          : 1000, 
        'chicagomag'        : 80, 
        'phillymag'         : 80, 
        'netflix'           : 100, 
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
    ])
    
    location_category_blacklist = set([
        'music', 
        'film', 
        'book', 
    ])
    
    location_subcategory_blacklist = set([
        'app', 
        'video_game', 
    ])
    
    def __init__(self, api):
        EntitySearcher.__init__(self)
        
        self.api = api
        self.entityDB = api._entityDB
        self.placesDB = api._placesEntityDB
        
        self.entityDB._collection.ensure_index([("title", pymongo.ASCENDING)])
        self.placesDB._collection.ensure_index([("coordinates", pymongo.GEO2D)])
        
        self._init_cities()
    
    def _init_cities(self):
        self._regions = {}
        city_in_state = {}
        
        for k, v in CityList.popular_cities.iteritems():
            if 'synonyms' in v:
                for synonym in v['synonyms']:
                    self._regions[synonym.lower()] = v
            
            v['name'] = k
            self._regions[k.lower()] = v
            
            state = v['state']
            if not state in city_in_state or v['population'] > city_in_state[state]['population']:
                city_in_state[state] = v
        
        # push lat/lng as best candidate for state
        for k, v in city_in_state.iteritems():
            self._regions[k.lower()] = v
        
        near_synonyms = set(['in', 'near'])
        self._near_synonym_res = []
        
        for synonym in near_synonyms:
            synonym_re = re.compile("(.*) %s ([a-z -']+)" % synonym)
            self._near_synonym_res.append(synonym_re)
    
    @lazyProperty
    def _googlePlaces(self):
        return GooglePlaces()
    
    @lazyProperty
    def _amazonAPI(self):
        return AmazonAPI()
    
    def getSearchResults(self, 
                         query, 
                         coords=None, 
                         limit=10, 
                         category_filter=None, 
                         subcategory_filter=None, 
                         full=False):
        input_query = query.strip().lower()
        original_coords = True
        
        query = input_query
        
        if not self._is_possible_location_query(category_filter, subcategory_filter):
            # if we're filtering by category / subcategory and the filtered results 
            # couldn't possibly contain a location, then ensure that coords is disabled
            coords = None
        else:
            # process 'in' or 'near' location hint
            for synonym_re in self._near_synonym_res:
                match = synonym_re.match(query)
                
                if match is not None:
                    groups = match.groups()
                    region_name = groups[1]
                    
                    if region_name in self._regions:
                        region = self._regions[region_name]
                        query  = groups[0]
                        coords = [ region['lat'], region['lng'], ]
                        original_coords = False
                        break
        
        query = query.replace('[', '\[?')
        query = query.replace(']', '\]?')
        query = query.replace('(', '\(?')
        query = query.replace(')', '\)?')
        query = query.replace('|', '\|')
        query = query.replace('.', '\.?')
        query = query.replace(':', ':?')
        query = query.replace('&', ' & ')
        
        # process individual words in query
        words = query.split(' ')
        if len(words) > 1:
            for i in xrange(len(words)):
                word = words[i]
                
                if word.endswith('s'):
                    word += '?'
                else:
                    word += 's?'
                
                #word = "(%s)?" % word
                words[i] = word
            query = string.joinfields(words, ' ').strip()
        
        query = query.replace(' ands? ', ' (and|&)? ')
        query = query.replace('-', '-?')
        query = query.replace(' ', '[ -]?')
        query = query.replace("'", "'?")
        query = query.replace("$", "[$st]?")
        query = query.replace("5", "[5s]?")
        query = query.replace("!", "[!li]?")
        
        data = {}
        data['input']       = input_query
        data['query']       = query
        data['coords']      = coords
        data['limit']       = limit
        data['category']    = category_filter
        data['subcategory'] = subcategory_filter
        data['full']        = full
        logs.debug(pformat(data))
        
        entity_query = {"title": {"$regex": query, "$options": "i"}}
        
        results = {}
        
        pool = Pool(8)
        wrapper = {}
        
        def _find_entity(ret):
            ret['db_results'] = self.entityDB._collection.find(entity_query)
        
        pool.spawn(_find_entity, wrapper)
        
        if coords is None:
            def _find_amazon(ret):
                amazon_results = self._amazonAPI.item_detail_search(Keywords=input_query, 
                                                                    SearchIndex='All', 
                                                                    Availability='Available', 
                                                                    transform=True)
                
                entities = self.api._entityMatcher.addMany(amazon_results)
                ret['amazon_results'] = list((e, -1) for e in entities)
            
            if full:
                pool.spawn(_find_amazon, wrapper)
            
            pool.join()
            
            if full:
                try:
                    amazon_results = wrapper['amazon_results']
                except KeyError:
                    amazon_results = []
                
                for result in amazon_results:
                    results[result[0].entity_id] = result
        else:
            earthRadius = 3959.0 # miles
            q = SON([('geoNear', 'places'), ('near', [float(coords[1]), float(coords[0])]), ('distanceMultiplier', earthRadius), ('spherical', True), ('query', entity_query)])
            
            def _find_places(ret):
                ret['place_results'] = self.placesDB._collection.command(q)
            
            def _find_google_places(ret):
                params = {
                    'name' : input_query, 
                }
                
                google_results = self._googlePlaces.getEntityResultsByLatLng(coords, params, True)
                entities = []
                output   = []
                
                if google_results is not None and len(google_results) > 0:
                    entities = self.api._entityMatcher.addMany(google_results)
                    
                    if entities is not None:
                        for entity in entities:
                            distance = utils.get_spherical_distance(coords, (entity.lat, entity.lng))
                            distance = distance * earthRadius
                            
                            output.append((entity, distance))
                
                ret['google_place_results'] = output
            
            if full:
                pool.spawn(_find_google_places, wrapper)
            
            # perform the requests concurrently
            pool.spawn(_find_places, wrapper)
            pool.join()
            
            try:
                place_results = wrapper['place_results']['results']
            except KeyError:
                place_results = []
            
            for doc in place_results:
                entity = self.placesDB._convertFromMongo(doc['obj'])
                result = (entity, doc['dis'])
                
                results[result[0].entity_id] = result
            
            if full:
                try:
                    google_place_results = wrapper['google_place_results']
                except KeyError:
                    google_place_results = []
                
                for result in google_place_results:
                    results[result[0].entity_id] = result
        
        # process the normal mongodb results
        for entity in wrapper['db_results']:
            e = self.entityDB._convertFromMongo(entity)
            
            results[e.entity_id] = (e, -1)
        
        results = results.values()
        
        # apply category filter to results
        if category_filter is not None:
            results = filter(lambda e: e[0].category == category_filter, results)
        
        # apply subcategory filter to results
        if subcategory_filter is not None:
            results = filter(lambda e: e[0].subcategory == subcategory_filter, results)
        
        if 0 == len(results):
            return results
        
        # sort the results based on a custom ranking function
        results = sorted(results, key=self._get_entity_weight_func(input_query), reverse=True)
        
        # optionally limit the number of results shown
        if limit is not None and limit >= 0:
            results = results[0 : min(len(results), limit)]
        
        # strip out distance from results if not using original (user's) coordinates
        if not original_coords:
            results = list((result[0], -1) for result in results)
        
        return results
    
    def _get_entity_weight_func(self, input_query):
        def _get_entity_weight(result):
            entity   = result[0]
            distance = result[1]
            
            title_value         = self._get_title_value(input_query, entity)
            subcategory_value   = self._get_subcategory_value(entity)
            source_value        = self._get_source_value(entity)
            quality_value       = self._get_quality_value(entity)
            distance_value      = self._get_distance_value(distance)
            
            title_weight        = 1.0
            subcategory_weight  = 0.5
            source_weight       = 0.4
            quality_weight      = 1.0
            distance_weight     = 1.5
            
            # TODO: revisit and iterate on this simple linear ranking formula
            aggregate_value     = title_value * title_weight + \
                                  subcategory_value * subcategory_weight + \
                                  source_value * source_weight + \
                                  quality_value * quality_weight + \
                                  distance_value * distance_weight
            
            data = {}
            data['title']       = entity.title
            data['titlev']      = title_value
            data['subcatv']     = subcategory_value
            data['sourcev']     = source_value
            data['qualityv']    = quality_value
            data['distancev']   = distance_value
            data['distance']    = distance
            data['totalv']      = aggregate_value
            
            #from pprint import pprint
            #pprint(data)
            
            return aggregate_value
        
        return _get_entity_weight
    
    def _get_title_value(self, input_query, entity):
        title  = entity.title.lower()
        weight = 1.0
        
        if input_query == title:
            # if the title is an 'exact' query match (case-insensitive), weight it heavily
            return 500
        elif input_query in title:
            if title.startswith(input_query):
                # if the query is a prefix match for the title, weight it more
                weight = 1.8
            else:
                weight = 1.2
        
        is_junk = " \t-".__contains__ # characters for SequenceMatcher to disregard
        ratio   = SequenceMatcher(is_junk, input_query, entity.title.lower()).ratio()
        value   = ratio * weight
        
        return value
    
    def _get_subcategory_value(self, entity):
        subcat = entity.subcategory
        
        try:
            weight = self.subcategory_weights[subcat]
        except KeyError:
            # default weight for non-standard subcategories
            weight = 30
        
        return weight / 100.0
    
    def _get_source_value(self, entity):
        sources = entity.sources
        
        source_value_sum = 0 #sum(self.source_weights[s] for s in sources)
        for source in sources:
            if source in self.source_weights:
                source_value_sum += self.source_weights[source]
            else:
                # default source value
                source_value_sum += 50
        
        return source_value_sum / 100.0
    
    def _get_quality_value(self, entity):
        value = 1.0
        
        """
        # Note: Disabling temporarily since it fails on multiple "popularity" items 
        # in schema
        if 'popularity' in entity:
            # popularity is in the range [1,1000]
            #print 'POPULARITY: %d' % (entity['popularity'], )
            value *= 5 * ((2000 - int(entity['popularity'])) / 1000.0)
        """
        
        return value
    
    def _get_distance_value(self, distance):
        if distance < 0:
            return 0
        
        x = (distance - 50)
        a = -0.4
        b = 2.8
        c = -6.3
        d = 4
        
        x2 = x * x
        x3 = x2 * x
        
        # simple cubic function of distance with the aim that 
        # distances nearby will be rated significantly higher 
        # than distances "far" away, with distances too far 
        # away being penalized very quickly as the distance 
        # grows.
        value = a * x3 + b * x2 + c * x + d
        
        # rescale
        if value > 0:
            value = math.log10(1 + value)
        else:
            value = -math.log10(1 - value)
        
        return value
    
    def _is_possible_location_query(self, category_filter, subcategory_filter):
        if category_filter is None and subcategory_filter is None:
            return True
        
        if category_filter in self.location_category_blacklist:
            return False
        
        if subcategory_filter in self.location_subcategory_blacklist:
            return False
        
        return True

