#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

class AEntityDatabase(object):
    
    def __init__(self):
        pass
    
    def addEntity(self, entity):
        pass
    
    def getEntity(self, entityID):
        pass
    
    def updateEntity(self, entity):
        pass
    
    def addEntities(self, entities):
        return map(self.createEntity, entities)
    
    def getEntities(self, entityIDs):
        return map(self.getEntity, entityIDs)
    
    def updateEntities(self, entities):
        return map(self.updateEntities, entities)

