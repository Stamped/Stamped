#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import logs, math, pymongo, re, string
import unicodedata, gevent
import CityList

from EntitySearcher import EntitySearcher
from Schemas        import Entity
from difflib        import SequenceMatcher
from pymongo.son    import SON
from gevent.pool    import Pool
from pprint         import pprint, pformat
from utils          import lazyProperty

# third-party search API wrappers
from GooglePlaces   import GooglePlaces
from libs.apple     import AppleAPI
from libs.AmazonAPI import AmazonAPI

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
        'song'              : 25, 
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
        'apple'             : 80, 
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
    
    location_category_blacklist = set([
        'music', 
        'film', 
        'book', 
    ])
    
    location_subcategory_blacklist = set([
        'book', 
        'movie', 
        'tv', 
        'artist', 
        'song', 
        'album', 
        'app', 
        'video_game', 
    ])
    
    amazon_category_blacklist = set([
        'food', 
    ])
    
    amazon_subcategory_whitelist = set([
        'book', 
        'movie', 
        'tv', 
        'artist', 
        'song', 
        'album', 
        'video_game', 
    ])
    
    apple_category_whitelist = set([
        'music', 
        'film', 
    ])
    
    apple_subcategory_whitelist = set([
        'movie', 
        'tv', 
        'artist', 
        'song', 
        'album', 
    ])
    
    def __init__(self, api):
        EntitySearcher.__init__(self)
        
        self.api = api
        self.entityDB = api._entityDB
        self.placesDB = api._placesEntityDB
        self.tempDB   = api._tempEntityDB
        self._statsSink = api._statsSink
        
        self.placesDB._collection.ensure_index([("coordinates", pymongo.GEO2D)])
        self.entityDB._collection.ensure_index([("titlel", pymongo.ASCENDING)])
        
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
    
    @lazyProperty
    def _appleAPI(self):
        return AppleAPI()
    
    def getSearchResults(self, 
                         query, 
                         coords=None, 
                         limit=10, 
                         category_filter=None, 
                         subcategory_filter=None, 
                         full=False, 
                         prefix=False):
        
        if prefix:
            assert not full
        
        # -------------------------------- #
        # transform input query and coords #
        # -------------------------------- #
        
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
        
        # attempt to replace accented characters with their ascii equivalents
        query = unicodedata.normalize('NFKD', unicode(query)).encode('ascii', 'ignore')
        
        if prefix:
            # perform a faster prefix-query by ensuring that any matching 
            # results begin with the given string as opposed to matching 
            # the given string anywhere in a result's title
            query = "^%s" % query
            
            query = query.replace('[', '\[')
            query = query.replace(']', '\]')
            query = query.replace('(', '\(')
            query = query.replace(')', '\)')
            query = query.replace('|', '\|')
            query = query.replace('.', '\.')
        else:
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
            query = query.replace("$", "[$st]?")
            query = query.replace("5", "[5s]?")
            query = query.replace("!", "[!li]?")
            query = query.replace('-', '[ -]?')
            query = query.replace(' ', '[ -]?')
            query = query.replace("'", "'?")
        
        query = query.replace('cafe', "caf[eé]")
        
        """
        data = {}
        data['input']       = input_query
        data['query']       = query
        data['coords']      = coords
        data['limit']       = limit
        data['category']    = category_filter
        data['subcategory'] = subcategory_filter
        data['full']        = full
        logs.debug(pformat(data))
        """
        
        #entity_query = {"title": {"$regex": query, "$options": "i"}}
        entity_query = {"titlel": {"$regex": query }}
        
        results = {}
        wrapper = {}
        asins   = set()
        gids    = set()
        aids    = set()
        pool    = Pool(8)
        
        # -------------------------------- #
        # initiate external search queries #
        # -------------------------------- #
        
        # search built-in entities database
        def _find_entity(ret):
            # only select certain fields to return to reduce data transfer
            fields = {
                'title' : 1, 
                'sources' : 1, 
                'subcategory' : 1, 
            }
            
            if prefix or len(input_query) < 3:
                db_results = self.entityDB._collection.find(entity_query, output=list, limit=100)
            else:
                db_results = self.entityDB._collection.find(entity_query, output=list)
            
            ret['db_results'] = []
            for doc in db_results:
                try:
                    e = self.entityDB._convertFromMongo(doc)
                    ret['db_results'].append((e, -1))
                except:
                    utils.printException()
        
        # search apple itunes API
        def _find_apple_specific(ret, media, entity):
            try:
                params = dict(
                    country='us', 
                    term=input_query, 
                    media=media, 
                    limit=5, 
                    transform=True
                )
                
                if entity is not None:
                    params['entity'] = entity
                
                self._statsSink.increment('stamped.api.search.third-party.apple')
                apple_results = self._appleAPI.search(**params)
                
                for result in apple_results:
                    entity = result.entity
                    
                    entity.entity_id = 'T_APPLE_%s' % entity.aid
                    ret['apple_results'].append((entity, -1))
            except:
                utils.printException()
        
        # search apple itunes API for multiple variants (artist, album, song, etc.)
        def _find_apple(ret):
            try:
                apple_pool = Pool(4)
                ret['apple_results'] = []
                
                if subcategory_filter is None or subcategory_filter == 'song':
                    apple_pool.spawn(_find_apple_specific, ret, media='music', entity='song')
                
                if subcategory_filter is None or subcategory_filter == 'album':
                    apple_pool.spawn(_find_apple_specific, ret, media='music', entity='album')
                
                if subcategory_filter is None or subcategory_filter == 'artist':
                    apple_pool.spawn(_find_apple_specific, ret, media='all', entity='allArtist')
                
                apple_pool.spawn(_find_apple_specific, ret, media='all', entity=None)
                apple_pool.join()
            except:
                utils.printException()
        
        # search amazon product API
        def _find_amazon(ret):
            try:
                self._statsSink.increment('stamped.api.search.third-party.amazon')
                amazon_results = self._amazonAPI.item_detail_search(Keywords=input_query, 
                                                                    SearchIndex='All', 
                                                                    Availability='Available', 
                                                                    transform=True)
                
                ret['amazon_results'] = []
                for entity in amazon_results:
                    entity.entity_id = 'T_AMAZON_%s' % entity.asin
                    ret['amazon_results'].append((entity, -1))
            except:
                utils.printException()
        
        if full:
            if self._is_possible_amazon_query(category_filter, subcategory_filter):
                pool.spawn(_find_amazon, wrapper)
            
            if self._is_possible_apple_query(category_filter, subcategory_filter):
                pool.spawn(_find_apple,  wrapper)
        
        pool.spawn(_find_entity, wrapper)
        
        # ------------------------------ #
        # handle location-based searches #
        # ------------------------------ #
        
        if coords is not None:
            earthRadius = 3959.0 # miles
            q_params = [
                ('geoNear', 'places'), 
                ('near', [float(coords[1]), float(coords[0])]), 
                ('distanceMultiplier', earthRadius), 
                ('spherical', True), 
                ('query', entity_query), 
            ]
            
            if prefix:
                fields = {
                    'title' : 1, 
                    'sources' : 1, 
                    'subcategory' : 1, 
                    'coordinates' : 1, 
                }
                
                # limit number of results returned
                q_params.append(('num', 50))
                
                # only select certain fields to return to reduce data transfer
                #q_params.append(('fields', fields))
            
            q = SON(q_params)
            
            # search built-in places database via proximity
            def _find_places(ret):
                place_results = self.placesDB._collection.command(q)
                
                try:
                    place_results = wrapper['place_results']['results']
                except KeyError:
                    place_results = []
                
                wrapper['place_results'] = []
                for doc in place_results:
                    try:
                        e = self.placesDB._convertFromMongo(doc['obj'])
                    except:
                        utils.printException()
                        continue
                    
                    wrapper['place_results'][e.entity_id] = (e, doc['dis'])
            
            # search Google Places API
            def _find_google_places(ret, specific_coords, radius, use_distance):
                try:
                    params = {
                        'name'   : input_query, 
                        'radius' : radius, 
                    }
                    
                    self._statsSink.increment('stamped.api.search.third-party.googlePlaces')
                    google_results = self._googlePlaces.getEntityResultsByLatLng(specific_coords, params, detailed=False)
                    entities = []
                    
                    if google_results is not None and len(google_results) > 0:
                        #utils.log(len(google_results))
                        
                        for entity in google_results:
                            if use_distance:
                                distance = utils.get_spherical_distance(coords, (entity.lat, entity.lng))
                                distance = distance * earthRadius
                            else:
                                distance = -1
                            
                            entity.entity_id = 'T_GOOGLE_%s' % entity.reference
                            ret['google_place_results'].append((entity, distance))
                except:
                    utils.printException()
            
            if full:
                wrapper['google_place_results'] = []
                pool.spawn(_find_google_places, wrapper, coords, 500, True)
                
                us_center_coords = [ 39.5, -98.35 ]
                us_search_radius = 5000000
                pool.spawn(_find_google_places, wrapper, us_center_coords, us_search_radius, False)
            
            pool.spawn(_find_places, wrapper)
        
        # perform the requests concurrently, yielding several advantages:
        #   1) fault isolation between separate requests s.t. if one query 
        #      fails or takes too long to complete, we can still return 
        #      results from the other queries.
        #   2) speed gain from performing requests asynchronously
        #   3) guarantee of the maximum amount of time any given search may take
        # 
        # note: timeout is specified in seconds
        # TODO: drive this timout number down to speed up search results!
        pool.join(timeout=4)
        
        # ----------------- #
        # parse all results #
        # ----------------- #
        
        def _add_result(result):
            try:
                # TODO: add an async task to merge these obvious dupes
                
                # dedupe entities from amazon
                asin = result[0].asin
                if asin is not None:
                    if asin in asins:
                        return
                    asins.add(asin)
                
                # dedupe entities from google
                gid = result[0].gid
                if gid is not None:
                    if gid in gids:
                        return
                    gids.add(gid)
                
                # dedupe entities from apple
                aid = result[0].aid
                if aid is not None:
                    if aid in aids:
                        return
                    aids.add(aid)
                
                results[result[0].entity_id] = result
            except:
                utils.printException()
        
        result_keys = [
            'place_results', 
            'db_results', 
            'apple_results', 
            'amazon_results', 
            'google_place_results', 
        ]
        
        # aggregate all results
        for key in result_keys:
            if key in wrapper:
                for result in wrapper[key]:
                    _add_result(result)
        
        # ----------------------- #
        # filter and rank results #
        # ----------------------- #
        
        results = results.values()
        #utils.log("num_results: %d" % len(results))
        
        # apply category filter to results
        if category_filter is not None:
            results = filter(lambda e: e[0].category == category_filter, results)
        
        # apply subcategory filter to results
        if subcategory_filter is not None:
            results = filter(lambda e: e[0].subcategory == subcategory_filter, results)
        
        # early-exit if there are no results at this point
        if 0 == len(results):
            return results
        
        # sort the results based on a custom ranking function
        results = sorted(results, key=self._get_entity_weight_func(input_query, prefix), reverse=True)
        
        # limit the number of results returned and remove obvious duplicates
        results = self._prune_results(results, limit)
        
        # strip out distance from results if not using original (user's) coordinates
        if not original_coords:
            results = list((result[0], -1) for result in results)
        
        if not prefix:
            gevent.spawn(self._add_temp, results)
        
        return results
    
    def _add_temp(self, results):
        """ retain a copy of all external entities in the 'tempentities' collection """
        
        for result in results:
            entity = result[0]
            
            if entity.entity_id.startswith('T_'):
                try:
                    entity.search_id = entity.entity_id
                    del entity.entity_id
                    
                    #utils.log("%s vs %s" % (entity.search_id, entity.entity_id))
                    self.tempDB.addEntity(entity)
                except:
                    # TODO: why is this occasionally failing?
                    utils.printException()
                    pass
    
    def _prune_results(self, results, limit):
        """ limit the number of results returned and remove obvious duplicates """
        
        #results = results[0: limit]
        #return results
        
        output = []
        prune  = set()
        
        if limit is not None:
            soft_limit = max(20, 2 * limit)
            
            if len(results) > soft_limit:
                results = results[0 : soft_limit]
        
        for i in xrange(len(results)):
            if i in prune:
                continue
            
            result1 = results[i]
            entity1 = result1[0]
            keep1   = True
            
            for j in xrange(i + 1, len(results)):
                if j in prune:
                    continue
                
                result2 = results[j]
                entity2 = result2[0]
                
                if entity1.subcategory == entity2.subcategory and \
                   entity1.title.lower() == entity2.title.lower():
                   prune.add(j)
                   
                   if keep1 and entity1.entity_id.startswith('T_') and not \
                       entity2.entity_id.startswith('T_'):
                       output.append(result2)
                       keep1 = False
            
            if keep1:
                output.append(result1)
            
            if limit is not None and len(output) >= limit:
                break
        
        return output
    
    def _get_entity_weight_func(self, input_query, prefix):
        """ 
            this wrapper func only exists to capture args for the 
            _get_entity_weight weighting function 
        """
        
        def _get_entity_weight(result):
            """
                returns a single floating point number representing the weighted 
                rank of this entity w.r.t. quality in this set of search results
            """
            
            entity   = result[0]
            distance = result[1]
            
            title_value         = self._get_title_value(input_query, entity, prefix)
            subcategory_value   = self._get_subcategory_value(entity)
            source_value        = self._get_source_value(entity)
            quality_value       = self._get_quality_value(entity)
            distance_value      = self._get_distance_value(distance)
            
            title_weight        = 1.0
            subcategory_weight  = 0.8
            source_weight       = 0.4
            quality_weight      = 1.0
            distance_weight     = 1.0
            
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
            
            #if input_query.lower() == entity.title.lower():
            #from pprint import pprint
            #pprint(entity.title)
            #pprint(data)
            
            return aggregate_value
        
        return _get_entity_weight
    
    def _get_title_value(self, input_query, entity, prefix):
        candidates = [ entity.title ]
        
        if (entity.subcategory == 'song' or entity.subcategory == 'album') and \
            'artist_display_name' in entity:
            candidates.append(entity.artist_display_name)
        
        try:
            if entity.subcategory == 'song' and entity.details.song.album_name is not None:
                candidates.append(entity.details.song.album_name)
        except:
            pass
        
        value_sum = 0.0
        
        for candidate in candidates:
            title  = candidate.lower()
            weight = 1.0
            
            if prefix:
                # for prefix-based searches, only take into account how well the 
                # equivalent prefix of the entity title matches, as opposed to the 
                # entity title overall
                if len(title) > len(input_query):
                    title = title[:len(input_query)]
            
            if not prefix and input_query == title:
                # if the title is an 'exact' query match (case-insensitive), weight it heavily
                value = 10
            else:
                if input_query in title:
                    if title.startswith(input_query):
                        # if the query is a prefix match for the title, weight it more
                        weight = 6
                    elif title.endswith(input_query):
                        weight = 4
                    elif 'remix' not in title:
                        weight = 1.4
                
                is_junk = " \t-".__contains__ # characters for SequenceMatcher to disregard
                ratio   = SequenceMatcher(is_junk, input_query, title).ratio()
                value   = ratio * weight
            
            value_sum = max(value_sum, value)
        
        return value_sum
    
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
                if source == 'netflix' and not 'nid' in source:
                    continue
                
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
            # popularity is in the range [1,1000] for iTunes entities
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
        if category_filter is not None and category_filter in self.location_category_blacklist:
            return False
        
        if subcategory_filter is not None and subcategory_filter in self.location_subcategory_blacklist:
            return False
        
        return True
    
    def _is_possible_amazon_query(self, category_filter, subcategory_filter):
        if category_filter is not None and category_filter in self.amazon_category_blacklist:
            return False
        
        if subcategory_filter is not None and subcategory_filter not in self.amazon_subcategory_whitelist:
            return False
        
        return True
    
    def _is_possible_apple_query(self, category_filter, subcategory_filter):
        if category_filter is not None and category_filter not in self.apple_category_whitelist:
            return False
        
        if subcategory_filter is not None and subcategory_filter not in self.apple_subcategory_whitelist:
            return False
        
        return True

