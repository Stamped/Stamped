#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from ATitleBasedEntityMatcher import ATitleBasedEntityMatcher
from Schemas                  import Entity
from errors                   import Fail

class FilmEntityMatcher(ATitleBasedEntityMatcher):
    def __init__(self, stamped_api, options):
        ATitleBasedEntityMatcher.__init__(self, stamped_api, options)
    
    def getDuplicateCandidates(self, entity):
        results = self._entityDB._collection.find({
            "subcategory" : entity.subcategory, 
        })
        
        return self._convertFromMongo(results)

