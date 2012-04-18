#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals, utils, logs, pymongo

from AMongoCollection import AMongoCollection
from Schemas import *

class MongoActivityObjectCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='activityobjects', 
                                        primary_key='activity_id', 
                                        obj=ActivityObject, 
                                        overflow=True)
    
    ### PUBLIC
    
    def addActivityObject(self, activity):
        return self._addObject(activity)
    
    def removeActivityObject(self, activityId):
        documentId = self._getObjectIdFromString(activityId)
        result = self._removeMongoDocument(documentId)
        return result
    
    def removeActivityObjects(self, activityIds):
        documentIds = map(self._getObjectIdFromString, activityIds)
        result = self._removeMongoDocuments(documentIds)
        return result

    def getActivityObject(self, activityId):
        documentId = self._getObjectIdFromString(activityId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)

    def getActivityObjects(self, activityIds, **kwargs):
        ids = map(self._getObjectIdFromString, activityIds)

        documents = self._getMongoDocumentsFromIds(ids, **kwargs)

        return map(self._convertFromMongo, documents)

    def getActivityIds(self, **kwargs):

        query = {}

        userId = kwargs.pop('userId', None)
        if userId is not None:
            query['user_id'] = userId 

        friendId = kwargs.pop('friendId', None)
        if friendId is not None:
            query['friend_id'] = friendId 

        stampId = kwargs.pop('stampId', None)
        if stampId is not None:
            query['stamp_id'] = stampId 

        entityId = kwargs.pop('entityId', None)
        if entityId is not None:
            query['entity_id'] = entityId 

        commentId = kwargs.pop('commentId', None)
        if commentId is not None:
            query['comment_id'] = commentId

        genre = kwargs.pop('genre', None)
        if genre is not None:
            query['genre'] = genre 

        documents = self._collection.find(query, fields={'_id' : 1})

        result = []
        for document in documents:
            result.append(self._getStringFromObjectId(document['_id']))
        return result

    def getActivityForUsers(self, userIds, **kwargs):
        since       = kwargs.pop('since', None)
        before      = kwargs.pop('before', None)
        limit       = kwargs.pop('limit', 20)

        query = { 'user_id' : {'$in' : userIds } }

        if since is not None and before is not None:
            query['timestamp.created'] = { '$gte' : since, '$lte' : before }
        elif since is not None:
            query['timestamp.created'] = { '$gte' : since }
        elif before is not None:
            query['timestamp.created'] = { '$lte' : before }

        documents = self._collection.find(query).sort('timestamp.created', pymongo.DESCENDING).limit(limit)

        return map(self._convertFromMongo, documents)


