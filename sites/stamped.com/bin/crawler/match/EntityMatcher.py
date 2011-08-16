#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils

from AEntityMatcher import AEntityMatcher
from TitleBasedEntityMatchers import *
from IDBasedEntityMatchers import *
from PlacesEntityMatcher import PlacesEntityMatcher

from utils import lazyProperty

__all__ = [
    "EntityMatcher", 
]

class EntityMatcher(AEntityMatcher):
    
    def __init__(self, stamped_api, options):
        AEntityMatcher.__init__(self, stamped_api, options)
    
    @lazyProperty
    def _places_matcher(self):
        return PlacesEntityMatcher(self.stamped_api, self.options)
    
    @lazyProperty
    def _apple_matcher(self):
        return AppleEntityMatcher(self.stamped_api, self.options)
    
    @lazyProperty
    def _fandango_matcher(self):
        return FandangoEntityMatcher(self.stamped_api, self.options)
    
    def getDuplicateCandidates(self, entity):
        matcher = self._get_matcher_for_entity(entity)
        return matcher.getDuplicateCandidates(entity)
    
    def getMatchingDuplicates(self, entity, candidate_entities):
        matcher = self._get_matcher_for_entity(entity)
        return matcher.getMatchingDuplicates(entity, candidate_entities)
    
    def getBestDuplicate(self, duplicates):
        matcher = self._get_matcher_for_entity(duplicates[0])
        return matcher.getBestDuplicate(duplicates)
    
    def _get_matcher_for_entity(self, entity):
        if 'apple' in entity:
            return self._apple_matcher
        if 'place' in entity:
            return self._places_matcher
        if 'fandango' in entity:
            return self._fandango_matcher
        
        from pprint import pprint
        pprint(entity)
        
        assert False
        return self._places_matcher

