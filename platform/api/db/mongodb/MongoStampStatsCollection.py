#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs import report

try:
    import pymongo
    from AMongoCollection               import AMongoCollection
    from api.Schemas                        import *
except:
    report()
    raise


class MongoStampStatsCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='stampstats', primary_key='stamp_id', obj=StampStats)
    
        self._collection.ensure_index([ ('score', pymongo.DESCENDING) ])
        self._collection.ensure_index([ ('last_stamped', pymongo.ASCENDING) ])
        self._collection.ensure_index([ ('kinds', pymongo.ASCENDING) ])
        self._collection.ensure_index([ ('types', pymongo.ASCENDING) ])
        self._collection.ensure_index([ ('lat', pymongo.ASCENDING), \
                                        ('lng', pymongo.ASCENDING) ])

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
    
    def removeStampStats(self, stampId):
        documentId = self._getObjectIdFromString(stampId)
        return self._removeMongoDocument(stampId)
    
    def removeStatsForStamps(self, stampIds):
        documentIds = map(self._getObjectIdFromString, stampIds)
        return self._removeMongoDocuments(documentIds)

    def _buildPopularQuery(self, **kwargs):
        kinds = kwargs.pop('kinds', None)
        types = kwargs.pop('types', None)
        since = kwargs.pop('since', None)
        viewport = kwargs.pop('viewport', None)
        entityId = kwargs.pop('entityId', None)

        query = {}

        if kinds is not None:
            query['kinds'] = {'$in': list(kinds)}

        if types is not None:
            query['types'] = {'$in': list(types)}

        if viewport is not None:
            query["lat"] = {
                "$gte" : viewport.lower_right.lat, 
                "$lte" : viewport.upper_left.lat, 
            }
            
            if viewport.upper_left.lng <= viewport.lower_right.lng:
                query["lng"] = { 
                    "$gte" : viewport.upper_left.lng, 
                    "$lte" : viewport.lower_right.lng, 
                }
            else:
                # handle special case where the viewport crosses the +180 / -180 mark
                query["$or"] = [{
                        "lng" : {
                            "$gte" : viewport.upper_left.lng, 
                        }, 
                    }, 
                    {
                        "lng" : {
                            "$lte" : viewport.lower_right.lng, 
                        }, 
                    }, 
                ]

        if entityId is not None:
            query['entity_id'] = entityId

        if since is not None:
            query['last_stamped'] = {'$gte': since}

        return query

    def getPopularStampIds(self, **kwargs):
        limit = kwargs.pop('limit', 1000)

        query = self._buildPopularQuery(**kwargs)

        documents = self._collection.find(query, fields=['_id']) \
                        .sort([('score', pymongo.DESCENDING)]) \
                        .limit(limit)

        return map(lambda x: self._getStringFromObjectId(x['_id']), documents)

    def getPopularStampStats(self, **kwargs):
        limit = kwargs.pop('limit', 1000)

        query = self._buildPopularQuery(**kwargs)

        documents = self._collection.find(query) \
                        .sort([('score', pymongo.DESCENDING)]) \
                        .limit(limit)

        return map(self._convertFromMongo, documents)



