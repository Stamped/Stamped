#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs import report

try:
    from AMongoCollection               import AMongoCollection
    from Schemas                        import *
except:
    report()
    raise


class MongoEntityStatsCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='entitystats', primary_key='entity_id', obj=EntityStats)
    
    ### PUBLIC
    
    def addEntityStats(self, stat):
        return self._addObject(stat)
    
    def getEntityStats(self, entityId):
        documentId = self._getObjectIdFromString(entityId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)
    
    def updateEntityStats(self, stat):
        return self.update(stat)
    
    def removeEntityStats(self, entityId):
        documentId = self._getObjectIdFromString(entityId)
        return self._removeMongoDocument(documentId)

    def updateNumStamps(self, entityId, numStamps):
        self._collection.update(
            { '_id' : self._getObjectIdFromString(entityId) }, 
            { '$set' : { 'num_stamps' : numStamps } }
        )
        return True

    def addToPopular(self, entityId, stampId):
        self._collection.update(
            { '_id' : self._getObjectIdFromString(entityId) }, 
            { '$addToSet' : { 'popular_stamps' : stampId } }
        )
        return True

    def removeFromPopular(self, entityId, stampId):
        self._collection.update(
            { '_id' : self._getObjectIdFromString(entityId) }, 
            { '$pull' : { 'popular_stamps' : stampId } }
        )
        return True

    def setPopular(self, entityId, stampIds):
        self._collection.update(
            { '_id' : self._getObjectIdFromString(entityId) }, 
            { '$set' : { 'popular_stamps' : stampIds } }
        )
        return True

