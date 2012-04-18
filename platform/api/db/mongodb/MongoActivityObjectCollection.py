#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

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
