#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from AEntityDB import AEntityDB
from Entity import Entity
import Globals, Utils

class ProxyEntityDB(AEntityDB):
    
    def __init__(self, targetEntityDB, proxyDesc):
        desc = 'Proxy %s(%s)' % (proxyDesc, str(targetEntityDB))
        AEntityDB.__init__(self, desc)    
        
        self._target = targetEntityDB
        self._pool   = Globals.threadPool
    
    def addEntity(self, entity):
        entityPrime = self._transformInput(entity)
        
        if entityPrime:
            return self._target.addEntity(entityPrime)
        else:
            return None
    
    def getEntity(self, entityID):
        return self._transformOutput(self._target.getEntity(entityID))
    
    def updateEntity(self, entity):
        entityPrime = self._transformInput(entity)
        
        if entityPrime:
            return self._target.updateEntity(entityPrime)
        else:
            return None
    
    def removeEntity(self, entityID):
        return self._target.removeEntity(entityID)
    
    def addEntities(self, entities):
        numEntities = Utils.count(entities)
        Utils.log("")
        Utils.log("[%s] transforming %d %s" % \
            (str(self), numEntities, Utils.numEntitiesToStr(numEntities)))
        Utils.log("")
        
        for entity in entities:
            self._pool.add_task(self._transformInput, entity)
        
        #entitiesPrime = (self._transformInput(entity) for entity in entities)
        #entitiesPrime = filter(lambda e: e is not None, entitiesPrime)
        #Utils.log("%s %s" % (str(type(entitiesPrime)), str(entitiesPrime)))
        
        self._pool.wait_completion()
        return self._target.addEntities(entities)
    
    def getEntities(self, entityIDs):
        return (self._transformOutput(e) for e in self._target.getEntities(entityIDs))
    
    def updateEntities(self, entities):
        for entity in entities:
            self._pool.add_task(self._transformInput, entity)
        
        return self._target.updateEntities(entities)
    
    def removeEntities(self, entityIDs):
        return self._target.removeEntities(entityIDs)
    
    def close(self, closeTarget=False):
        if closeTarget:
            self._target.close()
    
    def _transformInput(self, entity):
        return entity
    
    def _transformOutput(self, entity):
        return entity

