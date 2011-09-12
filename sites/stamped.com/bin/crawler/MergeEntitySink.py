#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils

from match.EntityMatcher    import EntityMatcher
from MongoStampedAPI        import MongoStampedAPI
from AEntitySink            import AEntitySink
from Schemas                import Entity
from pprint                 import pprint

from match.IDBasedEntityMatchers import OpenTableEntityMatcher

class MergeEntitySink(AEntitySink):
    
    def __init__(self):
        AEntitySink.__init__(self, "MergeEntitySink")
        
        self.stampedAPI = MongoStampedAPI()
        self.matcher    = OpenTableEntityMatcher(self.stampedAPI)
    
    def _processItem(self, item):
        assert isinstance(item, Entity)
        utils.log("merging item %s" % (item.title, ))
        
        self.matcher.addOne(item)
    
    def _processItems(self, items):
        for item in items:
            self._processItem(item)

