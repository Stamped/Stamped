#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract
from AEntitySink import AEntitySink

class AEntityDB(AEntitySink):
    
    def __init__(self):
        AEntitySink.__init__(self, "Entity DB")
    
    def _processItem(self, item):
        return self.addEntity(item)
    
    def _processItems(self, items):
        return self.addEntities(items)
    
    @abstract
    def addEntity(self, entity):
        raise NotImplementedError
    
    @abstract
    def getEntity(self, entityId):
        raise NotImplementedError
    
    @abstract
    def updateEntity(self, entity):
        raise NotImplementedError
    
    @abstract
    def removeEntity(self, entityId):
        raise NotImplementedError
    
    @abstract
    def removeCustomEntity(self, entityId, userId):
        raise NotImplementedError
    
    @abstract
    def addEntities(self, entities):
        raise NotImplementedError

