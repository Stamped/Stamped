#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from Entity import Entity

class AEntityDB(object):
    
    def __init__(self, desc):
        self._desc = desc
    
    def addEntity(self, entity):
        raise NotImplementedError
    
    def getEntity(self, entityID):
        raise NotImplementedError
    
    def updateEntity(self, entity):
        raise NotImplementedError
    
    def removeEntity(self, entityID):
        raise NotImplementedError
    
    def addEntities(self, entities):
        return map(self.addEntity, entities)
    
    def getEntities(self, entityIDs):
        return map(self.getEntity, entityIDs)
    
    def updateEntities(self, entities):
        return map(self.updateEntities, entities)
    
    def removeEntities(self, entityIDs):
        return map(self.removeEntity, entityIDs)
    
    def __len__(self):
        raise NotImplementedError
    
    def __str__(self):
        return self._desc

