#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import math, pymongo

from AEntitySearcher import AEntitySearcher
from MongoEntityCollection import MongoEntityCollection
from MongoPlacesEntityCollection import MongoPlacesEntityCollection

from difflib import SequenceMatcher
from pymongo.son import SON
from utils import abstract
from Entity import Entity

class MongoEntitySearcher(AEntitySearcher):
    subcategory_weights = {
        'restaurant' : 100, 
        'bar' : 90, 
        'book' : 50, 
        'movie' : 60, 
        'artist' : 60, 
        'song' : 20, 
        'album' : 25, 
        'app' : 15, 
        'other' : 10,
    }

    source_weights = {
        'googlePlaces' : 90, 
        'openTable' : 100, 
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
    }
    
    def __init__(self):
        AEntitySearcher.__init__(self)
        
        self.entityDB = MongoEntityCollection()
        self.placesDB = MongoPlacesEntityCollection()
        
        self.entityDB._collection.ensure_index([("title", pymongo.ASCENDING)])
    
    def getSearchResults(self, 
                         query, 
                         coords=None, 
                         limit=10, 
                         category_filter=None, 
                         subcategory_filter=None, 
                         full=None):
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
        query = query.replace(' and ', ' (and|&)? ')
        query = query.replace('-', '-?')
        query = query.replace(' ', '[ \t-_]?')
        query = query.replace("'", "'?")
        query = query.replace("$", "[$st]?")
        query = query.replace("5", "[5s]?")
        query = query.replace("!", "[!li]?")
        utils.log("query: %s" % query)
        
        entity_query = {"title": {"$regex": query, "$options": "i"}}
        db_results = self.entityDB._collection.find(entity_query).limit(250)
        
        results = []
        results_set = set()
        
        if coords is not None:
            # NOTE: geoNear uses lng/lat and coordinates *must* be stored in lng/lat order in underlying collection
            # TODO: enforce this constraint when storing into mongo
            
            earthRadius = 3959.0 # miles
            q = SON([('geoNear', 'places'), ('near', [coords[1], coords[0]]), ('num', 10), ('distanceMultiplier', earthRadius), ('spherical', True), ('query', entity_query)])
            
            ret = self.placesDB._collection.command(q)
            
            for doc in ret['results']:
                entity = Entity(self.entityDB._mongoToObj(doc['obj'], 'entity_id'))
                result = (entity, doc['dis'])
                
                results.append(result)
                results_set.add(entity.entity_id)
        
        for entity in db_results:
            e = Entity(self.entityDB._mongoToObj(entity, 'entity_id'))
            
            if e.entity_id not in results_set:
                results.append((e, -1))
        
        if category_filter is not None:
            results = filter(lambda e: e[0].category == category_filter, results)
        if subcategory_filter is not None:
            results = filter(lambda e: e[0].subcategory == subcategory_filter, results)
        
        if 0 == len(results):
            return results
        
        is_junk = " \t-".__contains__
        
        def _get_weight(result):
            entity   = result[0]
            distance = result[1]
            
            title_value         = SequenceMatcher(is_junk, input_query, entity.title.lower()).ratio()
            subcategory_value   = self._get_subcategory_value(entity)
            source_value        = self._get_source_value(entity)
            quality_value       = self._get_quality_value(entity)
            distance_value      = self._get_distance_value(distance)
            
            title_weight        = 1.0
            subcategory_weight  = 0.5
            source_weight       = 0.2
            quality_weight      = 1.0
            distance_weight     = 1.0
            
            # TODO: revisit and iterate on this simple linear ranking formula
            aggregate_value     = title_value * title_weight + \
                                  subcategory_value * subcategory_weight + \
                                  source_value * source_weight + \
                                  quality_value * quality_weight + \
                                  distance_value * distance_weight
            
            data = {}
            data['title']  = entity.title
            data['titlev'] = title_value
            data['subcatv'] = subcategory_value
            data['sourcev'] = source_value
            data['qualityv'] = quality_value
            data['distancev'] = distance_value
            data['totalv'] = aggregate_value
            
            #from pprint import pprint
            #pprint(data)
            
            return aggregate_value
        
        # sort the results based on the _get_weight function
        results = sorted(results, key=_get_weight, reverse=True)
        
        # optionally limit the number of results shown
        if limit is not None and limit >= 0:
            results = results[0 : min(len(results), limit)]
        
        return results
    
    def _get_subcategory_value(self, entity):
        subcat = entity.subcategory
        
        if subcat in self.subcategory_weights:
            weight = self.subcategory_weights[subcat]
        else:
            weight = 30
        
        return weight / 100.0

    def _get_source_value(self, entity):
        sources = entity.sources
        
        source_value_sum = 0 #sum(self.source_weights[s] for s in sources)
        for source in sources:
            if source in self.source_weights:
                source_value_sum += self.source_weights[source]
            else:
                source_value_sum += 80
        
        return source_value_sum / 100.0

    def _get_quality_value(self, entity):
        value = 1.0
        
        if 'popularity' in entity:
            # popularity is in the range [1,1000]
            value *= 5 * ((2000 - int(entity['popularity'])) / 1000.0)
        
        return value

    def _get_distance_value(self, distance):
        if distance < 0:
            return 0
        
        value = 1.0 / math.log1p(1 + distance)
        value = max(min(value, 100), 0)
        value = value ** 2
        return value

