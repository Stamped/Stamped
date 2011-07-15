#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from abc import abstractmethod
from Entity import Entity

class AEntityDB(object):
    
    def __init__(self, desc):
        self._desc = desc
        
    @abstractmethod
    def addEntity(self, entity):
        pass
    
    @abstractmethod
    def getEntity(self, entityID):
        pass
        
    @abstractmethod
    def updateEntity(self, entity):
        pass
        
    @abstractmethod
    def removeEntity(self, entity):
        pass
    
    @abstractmethod
    def addEntities(self, entities):
        pass
        
    @abstractmethod
    def matchEntities(self, query, limit=20):
        pass