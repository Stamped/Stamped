#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import math, pymongo, string

from EntitySearcher import EntitySearcher
from GooglePlaces   import GooglePlaces
from Schemas        import Entity
from difflib        import SequenceMatcher
from pymongo.son    import SON
from gevent.pool    import Pool
from pprint         import pprint
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
        
        # note: the following subcategories are from google places
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
        'university'        : 70, 
        'zoo'               : 65, 
    }
    
    source_weights = {
        'googlePlaces' : 50, 
        'amazon' : 90, 
        'openTable' : 110, 
        'factual' : 5, 
        'apple' : 75, 
        'zagat' : 95, 
        'urbanspoon' : 80, 
        'nymag' : 95, 
        'sfmag' : 95, 
        'latimes' : 80, 
        'bostonmag' : 90, 
        'fandango' : 1000, 
        'chicagomag' : 80, 
        'phillymag'  : 80, 
        'netflix'  : 100, 
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
    
    def __init__(self, api):
        EntitySearcher.__init__(self)
        
        self.api = api
        self.entityDB = api._entityDB
        self.placesDB = api._placesEntityDB
        
        self.entityDB._collection.ensure_index([("title", pymongo.ASCENDING)])
        self.placesDB._collection.ensure_index([("coordinates", pymongo.GEO2D)])
    
    @lazyProperty
    def _googlePlaces(self):
        return GooglePlaces()
    
    def getSearchResults(self, 
                         query, 
                         coords=None, 
                         limit=10, 
                         category_filter=None, 
                         subcategory_filter=None, 
                         full=False):
        input_query = query.strip().lower()
        
        query = input_query
        query = query.replace('[', '\[?')
        query = query.replace(']', '\]?')
        query = query.replace('(', '\(?')
        query = query.replace(')', '\)?')
        query = query.replace('|', '\|')
        query = query.replace('.', '\.?')
        query = query.replace(':', ':?')
        query = query.replace('&', ' & ')
        
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
        pprint(data)
        
        entity_query = {"title": {"$regex": query, "$options": "i"}}
        db_results = []
        
        results_set = set()
        results = []
        
        if coords is None:
            db_results = self.entityDB._collection.find(entity_query)
        else:
            pool = Pool(8)
            
            earthRadius = 3959.0 # miles
            q = SON([('geoNear', 'places'), ('near', [float(coords[1]), float(coords[0])]), ('distanceMultiplier', earthRadius), ('spherical', True), ('query', entity_query)])
            
            wrapper = {}
            def _find_places(ret):
                ret['place_results'] = self.placesDB._collection.command(q)
            
            def _find_entity(ret):
                ret['db_results'] = self.entityDB._collection.find(entity_query)
            
            def _find_google_places(ret):
                params = {
                    'name' : input_query, 
                }
                
                google_results = self._googlePlaces.getSearchResultsByLatLng(coords, params)
                entities = []
                output   = []
                
                if google_results is not None:
                    for result in google_results:
                        subcategory  = self._googlePlaces.getSubcategoryFromTypes(result['types'])
                        if subcategory not in self.google_subcategory_whitelist:
                            continue
                        
                        entity = Entity()
                        entity.title = result['name']
                        entity.image = result['icon']
                        entity.lat   = result['geometry']['location']['lat']
                        entity.lng   = result['geometry']['location']['lng']
                        entity.gid   = result['id']
                        entity.reference    = result['reference']
                        entity.subcategory  = subcategory
                        if 'vicinity' in result:
                            entity.neighborhood = result['vicinity']
                        
                        entities.append(entity)
                    
                    entities = self.api._entityMatcher.addMany(entities)
                    
                    if entities is not None:
                        for entity in entities:
                            distance = utils.get_spherical_distance(coords, (entity.lat, entity.lng))
                            distance = distance * earthRadius
                            
                            output.append((entity, distance))
                
                ret['google_place_results'] = output
            
            if full:
                pool.spawn(_find_google_places, wrapper)
            
            # perform the two db reads concurrently
            pool.spawn(_find_entity, wrapper)
            pool.spawn(_find_places, wrapper)
            
            pool.join()
            db_results = wrapper['db_results']
            
            try:
                place_results = wrapper['place_results']['results']
            except KeyError:
                place_results = []
            
            for doc in place_results:
                entity = self.placesDB._convertFromMongo(doc['obj'])
                result = (entity, doc['dis'])
                
                results.append(result)
                results_set.add(entity.entity_id)
            
            if full:
                try:
                    google_place_results = wrapper['google_place_results']
                except KeyError:
                    google_place_results = []
                
                for result in google_place_results:
                    results.append(result)
        
        for entity in db_results:
            # e = Entity(self.entityDB._mongoToObj(entity, 'entity_id'))
            e = self.entityDB._convertFromMongo(entity)
            
            if e.entity_id not in results_set:
                results.append((e, -1))
        
        if category_filter is not None:
            results = filter(lambda e: e[0].category == category_filter, results)
        if subcategory_filter is not None:
            results = filter(lambda e: e[0].subcategory == subcategory_filter, results)
        
        if 0 == len(results):
            return results
        
        def _get_weight(result):
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
            data['title']     = entity.title
            data['titlev']    = title_value
            data['subcatv']   = subcategory_value
            data['sourcev']   = source_value
            data['qualityv']  = quality_value
            data['distancev'] = distance_value
            data['distance']  = distance
            data['totalv']    = aggregate_value
            
            #from pprint import pprint
            #pprint(data)
            
            return aggregate_value
        
        # sort the results based on the _get_weight function
        results = sorted(results, key=_get_weight, reverse=True)
        
        # optionally limit the number of results shown
        if limit is not None and limit >= 0:
            results = results[0 : min(len(results), limit)]
        
        return results
    
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

