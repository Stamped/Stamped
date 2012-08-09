#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

import logs
from utils import lazyProperty

from db.mongodb.MongoEntityCollection import MongoEntityCollection
from db.mongodb.MongoEntityCollection import MongoEntityStatsCollection
from db.mongodb.MongoEntityCollection import MongoWhitelistedTastemakerEntityIdsCollection
from db.mongodb.MongoMenuCollection import MongoMenuCollection

class EntityDB(object):

    @lazyProperty
    def __entity_collection(self):
        return MongoEntityCollection()

    @lazyProperty
    def __menu_collection(self):
        return MongoMenuCollection()

    @lazyProperty
    def __entity_stats_collection(self):
        return MongoEntityStatsCollection()

    @lazyProperty
    def __whitelisted_tastemaker_entity_ids_collection(self):
        return MongoWhitelistedTastemakerEntityIdsCollection()


    def checkIntegrity(self, key, repair=False, api=None):
        return self.__entity_collection.checkIntegrity(key, repair=repair, api=api)
    
    ### ENTITIES

    def addEntity(self, entity):
        return self.__entity_collection.addEntity(entity)

    def addEntities(self, entities):
        return self.__entity_collection.addEntities(entities)

    def getEntity(self, entityId, forcePrimary=False):
        return self.__entity_collection.getEntity(entityId, forcePrimary=forcePrimary)

    def getEntities(self, entityIds):
        return self.__entity_collection.getEntities(entityIds)

    def getEntityMini(self, entityId):
        return self.__entity_collection.getEntityMini(entityId)

    def getEntityMinis(self, entityIds):
        return self.__entity_collection.getEntityMinis(entityIds)

    def getEntitiesByQuery(self, queryDict):
        return self.__entity_collection.getEntitiesByQuery(queryDict)

    def updateEntity(self, entity):
        return self.__entity_collection.updateEntity(entity)

    def removeEntity(self, entityId):
        return self.__entity_collection.removeEntity(entityId)

    def removeCustomEntity(self, entityId, userId):
        return self.__entity_collection.removeCustomEntity(entityId, userId)

    def updateDecoration(self, name, value):
        if name == 'menu':
            self.__menu_collection.updateMenu(value)

    def getWhitelistedTastemakerEntityIds(self, section):
        return self.__whitelisted_tastemaker_entity_ids_collection.getEntityIds(section)

    ### STATS
    
    def addEntityStats(self, stats):
        return self.__entity_stats_collection.addEntityStats(stats)
    
    def getEntityStats(self, entityId):
        return self.__entity_stats_collection.getEntityStats(entityId)
        
    def getStatsForEntities(self, entityIds):
        return self.__entity_stats_collection.getStatsForEntities(entityIds)
    
    def saveEntityStats(self, stats):
        return self.__entity_stats_collection.saveEntityStats(stats)
    
    def removeEntityStats(self, entityId):
        return self.__entity_stats_collection.removeEntityStats(entityId)
    
    def getPopularEntityStats(self, **kwargs):
        return self.__entity_stats_collection.getPopularEntityStats(**kwargs)
