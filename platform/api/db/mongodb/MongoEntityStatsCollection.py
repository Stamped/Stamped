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
    
    def addEntityStats(self, stats):
        return self._addObject(stats)
    
    def getEntityStats(self, entityId):
        documentId = self._getObjectIdFromString(entityId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)
    
    def updateEntityStats(self, stats):
        return self.update(stats)
    
    def removeEntityStats(self, entityId):
        documentId = self._getObjectIdFromString(entityId)
        return self._removeMongoDocument(documentId)

    def updateNumStamps(self, entityId, numStamps):
        self._collection.update(
            { '_id' : self._getObjectIdFromString(entityId) }, 
            { '$set' : { 'num_stamps' : numStamps } }
        )
        return True

    def setPopular(self, entityId, userIds):
        self._collection.update(
            { '_id' : self._getObjectIdFromString(entityId) }, 
            { '$set' : { 'popular_users' : userIds } }
        )
        return True

