#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
from errors import *

from ATitleBasedEntityMatcher import ATitleBasedEntityMatcher

from pymongo import GEO2D
from pymongo.son import SON

class PlacesEntityMatcher(ATitleBasedEntityMatcher):
    def __init__(self, stamped_api, options):
        ATitleBasedEntityMatcher.__init__(self, stamped_api, options)
        earthRadius = 3963.192 # miles
        maxDistance = 50.0 / earthRadius # convert to radians
        
        self.distance = maxDistance
        self._placesEntityDB._collection.ensure_index([("coordinates", GEO2D)])
    
    def getDuplicateCandidates(self, entity):
        if not 'lat' in entity or not 'lng' in entity:
            raise Fail('invalid entity')
        
        # TODO: verify lat / lng versus lng / lat
        q = SON({"$near" : [entity.lat, entity.lng]})
        q.update({"$maxDistance" : self.distance })
        
        docs     = self._placesEntityDB._collection.find({"coordinates" : q})
        entities = self._gen_entities(docs)
        
        return entities
    
    def _gen_entities(self, docs):
        for doc in docs:
            doc2 = self._entityDB._collection.find_one({ '_id' : doc['_id'] })
            if doc2 is not None:
                yield self._mongoToObj(doc2)

