#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from abc import abstractmethod
from Entity import Entity
from AEntitySink import AEntitySink

class AEntityDB(AEntitySink):
    
    def __init__(self, desc):
        AEntitySink.__init__(self, desc)
    
    def _processItem(self, item):
        return self.addEntity(item)
    
    def _processItems(self, items):
        return self.addEntities(items)
    
    @abstractmethod
    def addEntity(self, entity):
        raise NotImplementedError
    
    @abstractmethod
    def getEntity(self, entityID):
        raise NotImplementedError
    
    @abstractmethod
    def updateEntity(self, entity):
        raise NotImplementedError
    
    @abstractmethod
    def removeEntity(self, entity):
        raise NotImplementedError
    
    @abstractmethod
    def addEntities(self, entities):
        raise NotImplementedError
    
    @abstractmethod
    def matchEntities(self, query, limit=20):
        raise NotImplementedError

