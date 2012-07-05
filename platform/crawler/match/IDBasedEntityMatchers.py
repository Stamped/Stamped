#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from crawler.match.AIDBasedEntityMatcher import AIDBasedEntityMatcher

__all__ = [
    "AmazonEntityMatcher", 
    "AppleEntityMatcher", 
    "GooglePlacesEntityMatcher", 
    "FandangoEntityMatcher", 
    "OpenTableEntityMatcher", 
    "FactualEntityMatcher", 
    "TheTVDBMatcher", 
]

class AmazonEntityMatcher(AIDBasedEntityMatcher):
    def __init__(self, stamped_api, options=None):
        AIDBasedEntityMatcher.__init__(self, stamped_api, options, 'sources.amazon.asin')

class AppleEntityMatcher(AIDBasedEntityMatcher):
    def __init__(self, stamped_api, options=None):
        AIDBasedEntityMatcher.__init__(self, stamped_api, options, 'sources.apple.aid')

class GooglePlacesEntityMatcher(AIDBasedEntityMatcher):
    def __init__(self, stamped_api, options=None):
        AIDBasedEntityMatcher.__init__(self, stamped_api, options, 'sources.googlePlaces.gid')
    
    def getMatchingDuplicates(self, entity, candidate_entities):
        value   = self.getIDValue(entity)
        titlel  = entity.title.lower()
        
        return filter(lambda e: self.getIDValue(e) == value and e.title.lower() == titlel, candidate_entities)

class FandangoEntityMatcher(AIDBasedEntityMatcher):
    def __init__(self, stamped_api, options=None):
        AIDBasedEntityMatcher.__init__(self, stamped_api, options, 'sources.fandango.fid')

class OpenTableEntityMatcher(AIDBasedEntityMatcher):
    def __init__(self, stamped_api, options=None):
        AIDBasedEntityMatcher.__init__(self, stamped_api, options, 'sources.openTable.rid')

class FactualEntityMatcher(AIDBasedEntityMatcher):
    def __init__(self, stamped_api, options=None):
        AIDBasedEntityMatcher.__init__(self, stamped_api, options, 'sources.factual.factual_id')

class TheTVDBMatcher(AIDBasedEntityMatcher):
    def __init__(self, stamped_api, options=None):
        AIDBasedEntityMatcher.__init__(self, stamped_api, options, 'sources.thetvdb.thetvdb_id')

