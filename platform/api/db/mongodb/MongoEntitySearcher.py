#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import logs, math, pymongo, random, re, string
import unicodedata, gevent
import libs.worldcities

from EntitySearcher import EntitySearcher
from Schemas        import Entity
from difflib        import SequenceMatcher
from pymongo.son    import SON
from gevent.pool    import Pool
from pprint         import pprint, pformat
from utils          import lazyProperty
from errors         import StampedInputError

# third-party search API wrappers
from GooglePlaces   import GooglePlaces
from libs.apple     import AppleAPI
from libs.AmazonAPI import AmazonAPI
from libs.TheTVDB   import TheTVDB

from Entity         import setFields, isEqual, getSimplifiedTitle
from LRUCache       import lru_cache
from Memcache       import memcached_function
import tasks
import tasks.APITasks

# Stamped HQ coords: '40.736006685255155,-73.98884296417236'

class MongoEntitySearcher(EntitySearcher):
    # subcategory weights for biasing search results towards entities that we're 
    # most interested in.
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
        'album'             : 45, 
        
        # --------------------------
        #           other
        # --------------------------
        'app'               : 65, 
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
        'establishment'     : 5, 
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
    
    # weights for many of the built-in sources to bias results coming from 
    # higher quality sources as likely higher quality themselves as well
    source_weights = {
        'googlePlaces'      : 50, 
        'amazon'            : 80, 
        'openTable'         : 110, 
        'factual'           : 5, 
        'apple'             : 90, 
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
        'thetvdb'           : 110, 
    }
    
    # categories which definitely aren't associated with a location-based search
    location_category_blacklist = set([
        'music', 
        'film', 
        'book', 
    ])
    
    # subcategories which definitely aren't associated with a location-based search
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
    
    # categories which definitely won't come from amazon
    amazon_category_blacklist = set([
        'food', 
    ])
    
    # subcategories which may come from amazon
    amazon_subcategory_whitelist = set([
        'book', 
        'movie', 
        'tv', 
        'artist', 
        'song', 
        'album', 
        'video_game', 
    ])
    
    # categories which may come from apple
    apple_category_whitelist = set([
        'music', 
        'film', 
        'other', # apps
    ])
    
    # subcategories which may come from apple
    apple_subcategory_whitelist = set([
        'movie', 
        'tv', 
        'artist', 
        'song', 
        'album', 
        'app',
    ])
    
    _suffix_regexes = [
        re.compile('^(.*) \[[^\]]+\] *$'), 
        re.compile('^(.*) \([^)]+\) *$'), 
        re.compile('^(.*) \([^)]+\) *by +[A-Za-z. -]+$'), 
    ]
    
    _negative_title_strings = {
        '[vhs]'             : -1, 
        'special edition'   : -0.5, 
        '[dvd]'             : -1, 
        'blu-ray'           : -1, 
        'season'            : -1, 
        'complete series'   : -1, 
    }
    
    def __init__(self, api):
        EntitySearcher.__init__(self)
        self.api = api
        
        self.entityDB = api._entityDB
        self.placesDB = api._placesEntityDB
        self.tempDB   = api._tempEntityDB
        self.cacheDB  = api._searchCacheDB
        
        self._statsSink = api._statsSink
        self._errors    = utils.AttributeDict()
        self._notificationHandler = api._notificationHandler
        
        self.placesDB._collection.ensure_index([("coordinates", pymongo.GEO2D)])
        self.entityDB._collection.ensure_index([("titlel", pymongo.ASCENDING)])
        self.cacheDB._collection.ensure_index([("query", pymongo.ASCENDING)])
        
        libs.worldcities.try_get_region('ny')
    
    @lazyProperty
    def _googlePlaces(self):
        return GooglePlaces()
    
    @lazyProperty
    def _amazonAPI(self):
        return AmazonAPI()
    
    @lazyProperty
    def _appleAPI(self):
        return AppleAPI()
    
    @lazyProperty
    def _theTVDB(self):
        return TheTVDB()
    
    def _get_cache(self):
        return self.api._cache
    
    @lru_cache(maxsize=128)
    def getSearchResults(self, 
                         query, 
                         coords=None, 
                         limit=10, 
                         category_filter=None, 
                         subcategory_filter=None, 
                         full=False, 
                         prefix=False, 
                         local=False, 
                         user=None):
        
        # NOTE: remove -- strictly for testing!
        #full = False
        
        # -------------------------------- #
        # transform input query and coords #
        # -------------------------------- #
        
        if prefix:
            assert not full
        else:
            query = query.strip()
        
        if coords is not None:
            coords = self._parseCoords(coords)
        
        input_query     = query.lower()
        national_query  = input_query
        original_coords = True
        is_possible_location_query = self._is_possible_location_query(category_filter, 
                                                                      subcategory_filter, 
                                                                      local, prefix)
        
        query = input_query
        
        if not is_possible_location_query:
            # if we're filtering by category / subcategory and the filtered results 
            # couldn't possibly contain a location, then ensure that coords is disabled
            coords = None
        else:
            # process 'in' or 'near' location hint
            result = libs.worldcities.try_get_region(query)
            
            if result is not None:
                query, coords, region_name = result
                input_query = query
                utils.log("[search] using region %s at %s" % (region_name, coords))
        
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
        
        input_query = input_query.encode('utf-8')
        
        """
        data = {}
        data['input']       = input_query
        data['query']       = query
        data['coords']      = coords
        data['limit']       = limit
        data['category']    = category_filter
        data['subcategory'] = subcategory_filter
        data['full']        = full
        utils.log(pformat(data))
        """
        
        results     = {}
        wrapper     = {}
        db_wrapper  = {}
        asins       = set()
        gids        = set()
        aids        = set()
        thetvdb_ids = set()
        pool        = Pool(8)
        earthRadius = 3959.0 # miles
        
        # -------------------------------- #
        # initiate external search queries #
        # -------------------------------- #
        
        # search built-in entities database
        def _find_entity():
            if coords is not None:
                lat, lng = coords[0], coords[1]
            else:
                lat, lng = None, None
            
            db_wrapper['db_results'] = self._find_entity(input_query, query, lat, lng, prefix)
        
        # search apple itunes API for multiple variants (artist, album, song, etc.)
        def _find_apple():
            wrapper['apple_results'] = self._find_apple(input_query, subcategory_filter)
        
        # search amazon product API
        def _find_amazon():
            wrapper['amazon_results'] = self._find_amazon(input_query)
        
        # search thetvdb.com
        def _find_tv():
            wrapper['tv_results'] = self._find_tv(input_query)
        
        # search google places autocomplete
        def _find_google_national():
            wrapper['google_national_results'] = self._find_google_national(national_query)
        
        if full:
            if self._is_possible_amazon_query(category_filter, subcategory_filter, local):
                #search_amazon  = (category_filter == 'book' or category_filter == 'other')
                #search_amazon |= (random.random() < 0.33)
                #if search_amazon:
                
                pool.spawn(_find_amazon)
            
            if self._is_possible_apple_query(category_filter, subcategory_filter, local):
                pool.spawn(_find_apple)
            
            # note: disabling thetvdb api queries for now after crawling all english tv shows
            # as of 11/2/11
            #if self._is_possible_tv_query(category_filter, subcategory_filter, local):
            #    pool.spawn(_find_tv)
            
            if is_possible_location_query and not local:
                pool.spawn(_find_google_national)
        
        if len(query) > 0:
            pool.spawn(_find_entity)
        
        # ------------------------------ #
        # handle location-based searches #
        # ------------------------------ #
        
        if coords is not None:
            entity_query = self._get_entity_query(query)
            
            try:
                q_params = [
                    ('geoNear', 'places'), 
                    ('near', [float(coords[1]), float(coords[0])]), 
                    ('distanceMultiplier', earthRadius), 
                    ('spherical', True), 
                    ('query', entity_query), 
                ]
                
                if prefix:
                    # limit number of results returned
                    q_params.append(('num', 10))
                else:
                    q_params.append(('num', 20))
                
                q = SON(q_params)
            except:
                q = None
            
            # search built-in places database via proximity
            def _find_places(ret):
                place_results = self.placesDB._collection.command(q)
                
                try:
                    place_results = place_results['results']
                except KeyError:
                    place_results = []
                
                db_wrapper['place_results'] = []
                for doc in place_results:
                    try:
                        entity = self.placesDB._convertFromMongo(doc['obj'])
                    except:
                        utils.printException()
                        continue
                    
                    db_wrapper['place_results'].append((entity, doc['dis']))
            
            # search Google Places API
            def _find_google_places(ret, specific_coords, radius, use_distance):
                try:
                    params = {
                        'radius' : radius, 
                    }
                    
                    if len(input_query) > 0:
                        params['name'] = input_query
                    
                    self._statsSink.increment('stamped.api.search.third-party.googlePlaces')
                    google_results = self._googlePlaces.getEntityResultsByLatLng(specific_coords, params, detailed=False)
                    if google_results is None:
                        return
                    
                    entities = []
                    
                    if 0 == len(google_results):
                        # retry with (undocumented) max radius allowed by Google Places API
                        params['radius'] = 50000
                        self._statsSink.increment('stamped.api.search.third-party.googlePlaces')
                        google_results = self._googlePlaces.getEntityResultsByLatLng(specific_coords, params, detailed=False)
                    
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
                except Exception, e:
                    self._handle_search_error('googlePlaces', e)
                    utils.printException()
                else:
                    self._clear_search_errors('googlePlaces')
            
            if full:
                wrapper['google_place_results'] = []
                radius = 100 if local and 0 == len(query) else 20000
                pool.spawn(_find_google_places, wrapper, coords, radius, True)
                
                # TODO: look into using (deprecated) maps local search
                #       look into using autosuggest for national coverage
                
                # TODO: find a workaround for non-local place searches
                # national search centered in kansas
                #us_center_coords = [ 39.5, -98.35 ]
                #us_search_radius = 5000000
                #pool.spawn(_find_google_places, wrapper, us_center_coords, us_search_radius, False)
            
            if len(query) > 0 and q is not None:
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
        pool.join(timeout=6.5)
        
        # ----------------- #
        # parse all results #
        # ----------------- #
        
        def _add_result(result):
            # TODO: add an async task to merge these obvious dupes
            try:
                entity = result[0]
                if entity.entity_id is None:
                    if entity.search_id is not None:
                        entity.entity_id = entity.search_id
                    else:
                        return
                elif entity.search_id is not None:
                    del entity.search_id
                
                # if local search and result is too far away, discard it
                if local and abs(result[1]) > 30:
                    return
                
                # filter any custom entities
                generated_by = entity.generated_by 
                if generated_by is not None and generated_by != user:
                    return
                
                # dedupe entities from amazon
                asin = entity.asin
                if asin is not None:
                    if asin in asins:
                        return
                    asins.add(asin)
                
                # dedupe entities from google
                gid = entity.gid
                if gid is not None:
                    if gid in gids:
                        return
                    gids.add(gid)
                
                # dedupe entities from apple
                aid = entity.aid
                if aid is not None:
                    if aid in aids:
                        return
                    aids.add(aid)
                
                # dedupe entities from thetvdb
                thetvdb_id = entity.thetvdb_id
                if thetvdb_id is not None:
                    if thetvdb_id in thetvdb_ids:
                        return
                    thetvdb_ids.add(thetvdb_id)
                
                if local and not self._is_possible_location_query(entity.category, entity.subcategory, False, prefix):
                    return
                
                results[entity.entity_id] = result
            except:
                utils.printException()
        
        # aggregate all db results
        for key, value in db_wrapper.iteritems():
            utils.log("%s) %d (%s)" % (key, len(value), input_query))
            
            for result in value:
                #utils.log(result[0].entity_id)

                setFields(result[0])
                
                # apply category filter to results
                if category_filter is not None:
                    if result[0].category == category_filter:
                        _add_result(result)
                else:
                    _add_result(result)
        
        # aggregate all third-party results
        for key, value in wrapper.iteritems():
            utils.log("%s) %d" % (key, len(value)))
            
            for result in value:
                _add_result(result)
        
        # ----------------------- #
        # filter and rank results #
        # ----------------------- #
        
        results   = results.values()
        converted = False
        
        def _convert(r):
            for result in r:
                setFields(result[0])
        
        # apply category filter to results
        if category_filter is not None:
            if not converted:
                converted = True
                _convert(results)
            
            results = filter(lambda e: e[0].category == category_filter, results)
        
        # apply subcategory filter to results
        if subcategory_filter is not None:
            if not converted:
                converted = True
                _convert(results)
            
            results = filter(lambda e: e[0].subcategory == subcategory_filter, results)
        
        # early-exit if there are no results at this point
        if 0 == len(results):
            return results
        
        # sort the results based on a custom ranking function
        results = sorted(results, key=self._get_entity_weight_func(input_query, prefix), reverse=True)
        
        # limit the number of results returned and remove obvious duplicates
        results = self._prune_results(results, limit, prefix)
        
        # strip out distance from results if not using original (user's) coordinates
        if not original_coords:
            results = list((result[0], -1) for result in results)
        
        # TODO: make this more readable
        results = list((result[0], result[1] if result[1] >= 0 or result[1] == -1 else -result[1]) for result in results)
        
        if not prefix:
            tasks.invoke(tasks.APITasks._saveTempEntity, args=[map(lambda r: (r[0].value, r[1]), results)])
        
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
                    entity.entity_id = entity.search_id
                    #logs.info('Added %s to tempentities:\n%s\n' % (entity.entity_id,pformat(entity)))
                except:
                    # TODO: why is this occasionally failing?
                    if entity.search_id is not None:
                        entity.entity_id = entity.search_id
                    
                    utils.printException()
                    logs.warning('Error trying to add %s to tempentities:\n%s\n' % (entity.entity_id,pformat(entity)))
                    pass
            else:
                pass
                #logs.info('did not add %s to tempentities:\n%s\n'%(entity.entity_id,pformat(entity)))
    
    def _prune_results(self, results, limit, prefix):
        """ limit the number of results returned and remove obvious duplicates """
        
        #results = results[0: limit]
        #return results
        
        output = []
        prune  = set()
        
        if limit is not None:
            soft_limit = max(20, 2 * limit)
            
            if len(results) > soft_limit:
                results = results[0 : soft_limit]
        
        # TODO: bug where an exact-matched entity that is far away will replace 
        # another non-built-in result that is much closer!
        # need to fix this asap -- tweak how we tell that two entities are equal!
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
                
                # TODO: replace with generic *are these two entities equal* function
                # look at unique indices
                if isEqual(entity1, entity2, prefix):
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
    
    def _simplify(self, entity, title):
        title = getSimplifiedTitle(title)
        title = title.replace('-', ' ')
        
        if title.startswith('the '):
            title = title[4:]
        
        if title.endswith(' the'):
            title = title[:-4]
        
        if entity.subcategory == 'app':
            if title.endswith(' free') or title.endswith(' lite'):
                title = title[:-5]
            elif title.endswith(' pro'):
                title = title[:-4]
        
        for regex in self._suffix_regexes:
            match = regex.match(title)
            
            if match is not None:
                title = match.groups()[0]
        
        title = title.strip()
        
        if title.endswith(','):
            title = title[:-1]
        
        return title
    
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
            
            try:
                entity   = result[0]
                distance = result[1]
                
                # entity.simplified_title = self._simplify(entity, entity.title)
                
                title_value         = self._get_title_value(input_query, entity, prefix)
                negative_value      = self._get_negative_value(entity)
                subcategory_value   = self._get_subcategory_value(entity)
                source_value        = self._get_source_value(entity)
                quality_value       = self._get_quality_value(entity)
                distance_value      = self._get_distance_value(distance)
                
                title_weight        = 1.0
                negative_weight     = 1.0
                subcategory_weight  = 0.8
                source_weight       = 0.4
                quality_weight      = 1.0
                distance_weight     = 1.0
                
                # TODO: revisit and iterate on this simple linear ranking formula
                aggregate_value     = title_value * title_weight + \
                                      negative_value * negative_weight + \
                                      subcategory_value * subcategory_weight + \
                                      source_value * source_weight + \
                                      quality_value * quality_weight + \
                                      distance_value * distance_weight
                
                """
                entity.stats.titlev     = title_value
                entity.stats.subcatv    = subcategory_value
                entity.stats.sourcev    = source_value
                entity.stats.qualityv   = quality_value
                entity.stats.distancev  = distance_value
                entity.stats.totalv     = aggregate_value
                """
                
                """
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
                from pprint import pprint
                print
                pprint(entity.title)
                pprint(data)
                print
                """

                return aggregate_value
            except:
                utils.printException()
            
            return -1
        
        return _get_entity_weight
    
    def _get_title_value(self, input_query, entity, prefix):
        candidates = [ entity.title ] #, entity.simplified_title ]
        
        if (entity.subcategory == 'song' or entity.subcategory == 'album') and \
            'artist_display_name' in entity:
            candidates.append(self._simplify(entity, entity.artist_display_name))
        
        try:
            if entity.subcategory == 'song' and entity.details.song.album_name is not None:
                candidates.append(self._simplify(entity, entity.details.song.album_name))
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
                        weight = 6.0
                    elif title.endswith(input_query):
                        weight = 4
                    elif 'remix' not in title:
                        weight = 1.4
                
                is_junk = " \t-".__contains__ # characters for SequenceMatcher to disregard
                ratio   = SequenceMatcher(is_junk, input_query, title).ratio()
                value   = ratio * weight
            
            value_sum = max(value_sum, value)
        
        return value_sum
    
    def _get_negative_value(self, entity):
        title = entity.title.lower()
        value = 0.0
        
        for substring in self._negative_title_strings:
            if substring in title:
                value += self._negative_title_strings[substring]
        
        return value
    
    def _get_subcategory_value(self, entity):
        subcat = entity.subcategory
        
        try:
            weight = self.subcategory_weights[subcat]
        except KeyError:
            # default weight for non-standard subcategories
            weight = 5
        
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
        
        return max(value, 0)
    
    def _is_possible_location_query(self, category_filter, subcategory_filter, local, prefix):
        if prefix:
            return False
        
        if local:
            return True
        
        if category_filter is not None and category_filter in self.location_category_blacklist:
            return False
        
        if subcategory_filter is not None and subcategory_filter in self.location_subcategory_blacklist:
            return False
        
        return True
    
    def _is_possible_amazon_query(self, category_filter, subcategory_filter, local):
        if local:
            return False
        
        if category_filter is not None and category_filter in self.amazon_category_blacklist:
            return False
        
        if subcategory_filter is not None and subcategory_filter not in self.amazon_subcategory_whitelist:
            return False
        
        return True
    
    def _is_possible_apple_query(self, category_filter, subcategory_filter, local):
        if local:
            return False
        
        if category_filter is not None and category_filter not in self.apple_category_whitelist:
            return False
        
        if subcategory_filter is not None and subcategory_filter not in self.apple_subcategory_whitelist:
            return False
        
        return True
    
    def _is_possible_tv_query(self, category_filter, subcategory_filter, local):
        if local:
            return False
        
        if category_filter is not None and category_filter != 'film':
            return False
        
        if subcategory_filter is not None and subcategory_filter != 'tv':
            return False
        
        return True
    
    def _get_entity_query(self, query):
        #return {"title": {"$regex": query, "$options": "i"}}
        return {"titlel": {"$regex": query }, "sources.userGenerated": {'$exists': False}}
    
    @lru_cache(maxsize=64)
    def _find_entity(self, input_query, query, lat, lng, prefix):
        if lat is None or lng is None:
            coords = None
        else:
            coords = (lat, lng)
        
        output = []
        
        """
        # only select certain fields to return to reduce data transfer
        fields = {
            'title' : 1, 
            'sources' : 1, 
            'subcategory' : 1, 
        }
        """
        
        if prefix or len(input_query) <= 3:
            max_results = 100
        else:
            max_results = 200
        
        entity_query = self._get_entity_query(query)
        db_results = self.entityDB._collection.find(entity_query, output=list, limit=max_results)
        earthRadius = 3959.0 # miles
        
        for doc in db_results:
            try:
                e = self.entityDB._convertFromMongo(doc)
                distance = -1
                
                if coords is not None and e.lat is not None and e.lng is not None:
                    distance = utils.get_spherical_distance(coords, (e.lat, e.lng))
                    distance = abs(distance * earthRadius)
                
                #assert e.entity_id is not None
                output.append((e, distance))
            except Exception, e:
                self._handle_search_error('mongodb', e)
                utils.printException()
            else:
                self._clear_search_errors('mongodb')
        
        return output
    
    # note: these decorators add tiered caching to this function, such that 
    # results will be cached locally with a very small LRU cache of 64 items 
    # and also cached remotely via memcached with a TTL of 7 days
    @lru_cache(maxsize=64)
    @memcached_function('_get_cache', time=7*24*60*60)
    def _find_apple(self, input_query, subcategory_filter):
        output = []
        
        def _find_apple_specific(media, entity):
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
                    #print "HERE) %s" % entity.title
                    
                    entity.entity_id = 'T_APPLE_%s' % entity.aid
                    output.append((entity, -1))
            except Exception, e:
                self._handle_search_error('apple', e)
                utils.printException()
            else:
                self._clear_search_errors('apple')
        
        try:
            apple_pool = Pool(4)
            
            # search for matching artists
            if subcategory_filter is None or subcategory_filter == 'artist':
                apple_pool.spawn(_find_apple_specific, media='music', entity='musicArtist')
            
            # search for misc matches that might not have been returned above
            apple_pool.spawn(_find_apple_specific, media='all', entity=None)
            
            # search for matching albums
            if subcategory_filter is None or subcategory_filter == 'album':
                apple_pool.spawn(_find_apple_specific, media='music', entity='album')
            
            # search for matching songs
            if subcategory_filter is None or subcategory_filter == 'song':
                apple_pool.spawn(_find_apple_specific, media='music', entity='song')
            
            # search for matching apps
            if subcategory_filter is None or subcategory_filter == 'app':
                apple_pool.spawn(_find_apple_specific, media='software', entity=None)
            
            apple_pool.join(timeout=6.5)
        except:
            utils.printException()
        
        return output
    
    # note: these decorators add tiered caching to this function, such that 
    # results will be cached locally with a very small LRU cache of 64 items 
    # and also cached remotely via memcached with a TTL of 7 days
    @lru_cache(maxsize=64)
    @memcached_function('_get_cache', time=7*24*60*60)
    def _find_amazon(self, input_query):
        output = []
        
        try:
            #utils.log("amazon")
            self._statsSink.increment('stamped.api.search.third-party.amazon')
            amazon_results = self._amazonAPI.item_detail_search(Keywords=input_query, 
                                                                SearchIndex='All', 
                                                                Availability='Available', 
                                                                transform=True)
            
            #utils.log("amazon: %d" % len(amazon_results))
            
            for entity in amazon_results:
                entity.entity_id = 'T_AMAZON_%s' % entity.asin
                output.append((entity, -1))
        except Exception, e:
            self._handle_search_error('amazon', e)
            utils.printException()
        else:
            self._clear_search_errors('amazon')
        
        return output
    
    # note: these decorators add tiered caching to this function, such that 
    # results will be cached locally with a very small LRU cache of 64 items 
    # and also cached remotely via memcached with a TTL of 7 days
    @lru_cache(maxsize=64)
    @memcached_function('_get_cache', time=7*24*60*60)
    def _find_tv(self, input_query):
        output = []
        
        try:
            self._statsSink.increment('stamped.api.search.third-party.thetvdb')
            results = self._theTVDB.search(input_query, detailed=False)
            
            for entity in results:
                entity.entity_id = 'T_TVDB_%s' % entity.thetvdb_id
                output.append((entity, -1))
        except Exception, e:
            self._handle_search_error('thetvdb', e)
            utils.printException()
        else:
            self._clear_search_errors('thetvdb')
        
        return output
    
    # note: these decorators add tiered caching to this function, such that 
    # results will be cached locally with a very small LRU cache of 64 items 
    # and also cached remotely via memcached with a TTL of 28 days
    @lru_cache(maxsize=64)
    @memcached_function('_get_cache', time=28*24*60*60)
    def _find_google_national(self, input_query):
        output = []
        
        try:
            self._statsSink.increment('stamped.api.search.third-party.googleAutocomplete')
            results = self._googlePlaces.getEntityAutocompleteResults(input_query)
            
            if results is not None:
                for entity in results:
                    entity.entity_id = 'T_GOOGLE_%s' % entity.reference
                    output.append((entity, -1))
        except Exception, e:
            self._handle_search_error('googleAutocomplete', e)
            utils.printException()
        else:
            self._clear_search_errors('googleAutocomplete')
        
        return output
    
    def _parseCoords(self, coords):
        if coords is not None and isinstance(coords, basestring):
            lat, lng = coords.split(',')
            coords = [ float(lat), float(lng) ]
        elif coords is not None and 'lat' in coords and coords.lat is not None:
            try:
                coords = [coords['lat'], coords['lng']]
                
                if coords[0] is None or coords[1] is None:
                    raise
            except:
                msg = "Invalid coordinates (%s)" % coords
                logs.warning(msg)
                raise StampedInputError(msg)
        else:
            return None
        return coords
    
    def _handle_search_error(self, key, error):
        if key not in self._errors:
            self._errors[key] = []
        
        detail = utils.getFormattedException()
        
        self._errors[key].append((error, detail))
        self._statsSink.increment('stamped.api.search.third-party.errors.%s' % key)
        utils.log("%s search failed (%s)" % (key, error))
        utils.log("%s search failed (%s)" % (key, detail))
        
        if 6 == len(self._errors[key]):
            subject = "%s search failing" % key
            message = "%s search failing\n\n" % key
            
            for error in self._errors[key]:
                message += "%s\n%s\n\n" % (error[0], error[1])
            
            self._notificationHandler.email(subject, message)
    
    def _clear_search_errors(self, key):
        if key in self._errors:
            self._errors[key] = []

