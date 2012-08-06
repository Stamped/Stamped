#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract
from api.AEntitySink import AEntitySink

class APlacesEntityDB(AEntitySink):
    
    def __init__(self):
        AEntitySink.__init__(self, "Places Entity DB")
    
    def _processItem(self, item):
        return self.addEntity(item)
    
    def _processItems(self, items):
        return self.addEntities(items)
    
    @abstract
    def addEntity(self, entity):
        raise NotImplementedError
    
    @abstract
    def getEntity(self, entityID):
        raise NotImplementedError
    
    @abstract
    def updateEntity(self, entity):
        raise NotImplementedError
    
    @abstract
    def removeEntity(self, entity):
        raise NotImplementedError
    
    @abstract
    def addEntities(self, entities):
        raise NotImplementedError
    
    @abstract
    def searchEntities(self, query, limit=20):
        raise NotImplementedError

