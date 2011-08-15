#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
from AEntityMatcher import AEntityMatcher

class AIDBasedEntityMatcher(AEntityMatcher):
    
    def __init__(self, stamped_api, id_key):
        AEntityMatcher.__init__(self, stamped_api)
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
        results = self._entityDB.find({ self.id_key, value })
        
        return self._mongoToObj(results)
    
    def getMatchingDuplicates(self, entity, candidate_entities):
        value   = self.getIDValue(entity)
        
        return filter(lambda e: self.getIDValue(e) == value, candidate_entities)

# ------------------------------------------------------------------------------

class AppleEntityMatcher(AIDBasedEntityMatcher):
    def __init__(self, stamped_api):
        AIDBasedEntityMatcher.__init__(self, stamped_api, 'sources.apple.aid')

class GooglePlacesEntityMatcher(AIDBasedEntityMatcher):
    def __init__(self, stamped_api):
        AIDBasedEntityMatcher.__init__(self, stamped_api, 'sources.googlePlaces.gid')

class FandangoEntityMatcher(AIDBasedEntityMatcher):
    def __init__(self, stamped_api):
        AIDBasedEntityMatcher.__init__(self, stamped_api, 'sources.fandango.fid')

class OpenTableEntityMatcher(AIDBasedEntityMatcher):
    def __init__(self, stamped_api):
        AIDBasedEntityMatcher.__init__(self, stamped_api, 'sources.openTable.rid')

class FactualEntityMatcher(AIDBasedEntityMatcher):
    def __init__(self, stamped_api):
        AIDBasedEntityMatcher.__init__(self, stamped_api, 'sources.factual.faid')

