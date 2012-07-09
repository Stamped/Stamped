#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from crawler.match.AEntityMatcher import AEntityMatcher

__all__ = [
    "AIDBasedEntityMatcher", 
]

class AIDBasedEntityMatcher(AEntityMatcher):
    
    def __init__(self, stamped_api, options, id_key):
        AEntityMatcher.__init__(self, stamped_api, options)
        self.id_key = id_key
        if '.' in id_key:
            self.entity_id_key = id_key[id_key.rfind('.') + 1:]
        else:
            self.entity_id_key = id_key
    
    def getIDValue(self, entity):
        assert self.entity_id_key in entity
        
        return entity[self.entity_id_key]
    
    def getDuplicateCandidates(self, entity):
        value   = self.getIDValue(entity)
        results = self._entityDB._collection.find({ self.id_key : value })
        
        return self._convertFromMongo(results)
    
    def getMatchingDuplicates(self, entity, candidate_entities):
        value   = self.getIDValue(entity)
        
        return filter(lambda e: self.getIDValue(e) == value, candidate_entities)

