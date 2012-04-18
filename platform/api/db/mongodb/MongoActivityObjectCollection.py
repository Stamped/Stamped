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

    def getActivityObject(self, activityId):
        documentId = self._getObjectIdFromString(activityId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)

    def getActivityObjects(self, activityIds, **kwargs):
        ids = map(self._getObjectIdFromString, activityIds)

        documents = self._getMongoDocumentsFromIds(ids, **kwargs)

        return map(self._convertFromMongo, documents)

    def matchActivityObject(self, activityObject):

        query = { 'genre' : activityObject.genre }

        if activityObject.user_id is not None:
            query['user_id'] = activityObject.user_id

        if activityObject.entity_id is not None:
            query['entity_id'] = activityObject.entity_id

        if activityObject.stamp_id is not None:
            query['stamp_id'] = activityObject.stamp_id 

        if activityObject.comment_id is not None:
            query['comment_id'] = activityObject.comment_id  

        activity = self._collection.find_one(query)
        assert activity is not None

        return activity
