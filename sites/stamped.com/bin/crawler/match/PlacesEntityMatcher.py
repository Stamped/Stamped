#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
from errors import *

from ATitleBasedEntityMatcher import ATitleBasedEntityMatcher
from Entity import Entity

from difflib import SequenceMatcher
from pymongo import GEO2D
from pymongo.son import SON

class PlacesEntityMatcher(ATitleBasedEntityMatcher):
    def __init__(self, stamped_api, options):
        ATitleBasedEntityMatcher.__init__(self, stamped_api, options)
        earthRadius = 3959.0 # miles
        maxDistance = 50.0 / earthRadius # convert to radians
        
        self.distance = maxDistance
        self._placesDB._collection.ensure_index([("coordinates", GEO2D)])
    
    def getDuplicateCandidates(self, entity):
        if not 'lat' in entity or not 'lng' in entity:
            raise Fail('invalid entity')
        
        # TODO: verify lat / lng versus lng / lat
        q = SON({"$near" : [entity.lng, entity.lat]})
        q.update({"$maxDistance" : self.distance })
        
        docs     = self._placesDB._collection.find({"coordinates" : q}, output=list)
        entities = self._gen_entities(docs)
        
        return entities
    
    def _gen_entities(self, docs):
        return (Entity(self._placesDB._mongoToObj(doc, 'entity_id')) for doc in docs)

