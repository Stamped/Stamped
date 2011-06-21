#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from Entity import Entity
from db.mysql.MySQLEntityDB import *

class AEntityDB(object):
    
    def __init__(self, desc):
        self._desc = desc
    
    def addEntity(self, entity):
        pass
    
    def getEntity(self, entityID):
        pass
    
    def updateEntity(self, entity):
        pass
    
    def removeEntity(self, entityID):
        pass
    
    def addEntities(self, entities):
        return map(self.addEntity, entities)
    
    def getEntities(self, entityIDs):
        return map(self.getEntity, entityIDs)
    
    def updateEntities(self, entities):
        return map(self.updateEntities, entities)
    
    def removeEntities(self, entityIDs):
        return map(self.removeEntity, entityIDs)
    
    def close(self):
        pass
    
    def __len__(self):
        pass
    
    def __str__(self):
        return self._desc

