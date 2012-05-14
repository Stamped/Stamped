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


class MongoStampStatsCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='stampstats', primary_key='stamp_id', obj=StampStats)
    
    ### PUBLIC
    
    def addStampStats(self, stats):
        return self._addObject(stats)
    
    def getStampStats(self, stampId):
        documentId = self._getObjectIdFromString(stampId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)

    def getStatsForStamps(self, stampIds):
        documentIds = map(self._getObjectIdFromString, stampIds)
        documents = self._getMongoDocumentsFromIds(documentIds)
        return map(self._convertFromMongo, documents)
    
    def updateStampStats(self, stats):
        return self.update(stats)

    def saveStampStats(self, stats):
        document = self._convertToMongo(stats)
        self._collection.save(document, safe=True)
        return self._convertFromMongo(document)
    
    def removeStampStats(self, entityId):
        documentId = self._getObjectIdFromString(entityId)
        return self._removeMongoDocument(documentId)

    # def updateNumStamps(self, entityId, numStamps):
    #     self._collection.update(
    #         { '_id' : self._getObjectIdFromString(entityId) }, 
    #         { '$set' : { 'num_stamps' : numStamps } }
    #     )
    #     return True

    # def setPopular(self, entityId, userIds):
    #     self._collection.update(
    #         { '_id' : self._getObjectIdFromString(entityId) }, 
    #         { '$set' : { 'popular_users' : userIds } }
    #     )
    #     return True

