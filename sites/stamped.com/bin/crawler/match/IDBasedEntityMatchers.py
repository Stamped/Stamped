#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
from AIDBasedEntityMatcher import AIDBasedEntityMatcher

__all__ = [
    "AppleEntityMatcher", 
    "GooglePlacesEntityMatcher", 
    "FandangoEntityMatcher", 
    "OpenTableEntityMatcher", 
    "FactualEntityMatcher", 
]

class AppleEntityMatcher(AIDBasedEntityMatcher):
    def __init__(self, stamped_api, options):
        AIDBasedEntityMatcher.__init__(self, stamped_api, options, 'sources.apple.aid')

class GooglePlacesEntityMatcher(AIDBasedEntityMatcher):
    def __init__(self, stamped_api, options):
        AIDBasedEntityMatcher.__init__(self, stamped_api, options, 'sources.googlePlaces.gid')

class FandangoEntityMatcher(AIDBasedEntityMatcher):
    def __init__(self, stamped_api, options):
        AIDBasedEntityMatcher.__init__(self, stamped_api, options, 'sources.fandango.fid')

class OpenTableEntityMatcher(AIDBasedEntityMatcher):
    def __init__(self, stamped_api, options):
        AIDBasedEntityMatcher.__init__(self, stamped_api, options, 'sources.openTable.rid')

class FactualEntityMatcher(AIDBasedEntityMatcher):
    def __init__(self, stamped_api, options):
        AIDBasedEntityMatcher.__init__(self, stamped_api, options, 'sources.factual.faid')

