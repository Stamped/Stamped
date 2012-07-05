#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from crawler.match.ATitleBasedEntityMatcher import ATitleBasedEntityMatcher

__all__ = [
    "ZagatEntityMatcher", 
    "UrbanspoonEntityMatcher", 
    "NYMagEntityMatcher", 
    "SFMagEntityMatcher", 
    "LATimesEntityMatcher", 
    "BostonMagEntityMatcher", 
]

class ATitleSourceBasedEntityMatcher(ATitleBasedEntityMatcher):
    def __init__(self, stamped_api, options, source):
        ATitleBasedEntityMatcher.__init__(self, stamped_api, options)
        
        self.source = source
    
    def getDuplicateCandidates(self, entity):
        results = self._entityDB._collection.find({ self.source : { "$exists" : True }})
        
        return self._convertFromMongo(results)

class ZagatEntityMatcher(ATitleSourceBasedEntityMatcher):
    def __init__(self, stamped_api, options):
        ATitleSourceBasedEntityMatcher.__init__(self, stamped_api, options, 'sources.zagat')

class UrbanspoonEntityMatcher(ATitleSourceBasedEntityMatcher):
    def __init__(self, stamped_api, options):
        ATitleSourceBasedEntityMatcher.__init__(self, stamped_api, options, 'sources.urbanspoon')

class NYMagEntityMatcher(ATitleSourceBasedEntityMatcher):
    def __init__(self, stamped_api, options):
        ATitleSourceBasedEntityMatcher.__init__(self, stamped_api, options, 'sources.nymag')

class SFMagEntityMatcher(ATitleSourceBasedEntityMatcher):
    def __init__(self, stamped_api, options):
        ATitleSourceBasedEntityMatcher.__init__(self, stamped_api, options, 'sources.sfmag')

class LATimesEntityMatcher(ATitleSourceBasedEntityMatcher):
    def __init__(self, stamped_api, options):
        ATitleSourceBasedEntityMatcher.__init__(self, stamped_api, options, 'sources.latimes')

class BostonMagEntityMatcher(ATitleSourceBasedEntityMatcher):
    def __init__(self, stamped_api, options):
        ATitleSourceBasedEntityMatcher.__init__(self, stamped_api, options, 'sources.bostonmag')

