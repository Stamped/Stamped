#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
from utils import abstract

class AEntityMatcher(object):
    """
        Abstract base class for finding and matching duplicate entities.
    """
    
    def __init__(self, stamped_api):
        self.stamped_api = stamped_api
    
    @property
    def _entityDB(self):
        return self.stamped_api._entityDB
    
    @property
    def _placesEntityDB(self):
        return self.stamped_api._placesEntityDB
    
    def getDuplicates(self, entity):
        candidate_entities = self.getDuplicateCandidates(entity)
        return self.getMatchingDuplicates(entity, candidate_entities)
    
    @abstract
    def getDuplicateCandidates(self, entity):
        pass
    
    @abstract
    def getMatchingDuplicates(self, entity, candidate_entities):
        pass
    
    def _mongoToObj(self, mongo):
        if isinstance(mongo, (list, tuple)):
            return map(self._mongoToObj, mongo)
        
        return Entity(self._entityDB._mongoToObj(mongo, 'entity_id'))

