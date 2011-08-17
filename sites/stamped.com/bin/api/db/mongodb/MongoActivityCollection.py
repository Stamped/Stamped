#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, logs

from datetime import datetime
from utils import lazyProperty

from AMongoCollection import AMongoCollection
from MongoUserActivityCollection import MongoUserActivityCollection

from api.AActivityDB import AActivityDB
from api.Activity import Activity

class MongoActivityCollection(AMongoCollection, AActivityDB):
    
    """
    Activity Types:
    * restamp
    * comment
    * reply
    * favorite
    * directed
    * mention
    * milestone
    """
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='activity')
        AActivityDB.__init__(self)
    
    def _convertToMongo(self, activity):
        document = activity.exportSparse()
        if 'activity_id' in document:
            document['_id'] = self._getObjectIdFromString(document['activity_id'])
            del(document['activity_id'])
        return document

    def _convertFromMongo(self, document):
        if '_id' in document:
            document['activity_id'] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])
        return Activity(document)
    
    ### PUBLIC
    
    @lazyProperty
    def user_activity_collection(self):
        return MongoUserActivityCollection()
    
    def getActivity(self, userId, **kwargs):
        params = {
            'since':    kwargs.pop('since', None),
            'before':   kwargs.pop('before', None), 
            'limit':    kwargs.pop('limit', 20),
            'sort':     'timestamp.created',
        }

        # Get activity
        activityIds = self.user_activity_collection.getUserActivityIds(userId)

        logs.debug("ACTIVITY IDS: %s" % activityIds)

        documentIds = []
        for activityId in activityIds:
            documentIds.append(self._getObjectIdFromString(activityId))

        logs.debug("DOCUMENT IDS: %s" % documentIds)

        # Get stamps
        documents = self._getMongoDocumentsFromIds(documentIds, **params)

        activity = []
        for document in documents:
            activity.append(self._convertFromMongo(document))

        return activity

    def addActivity(self, recipientIds, activity):
        document = self._convertToMongo(activity)
        document = self._addMongoDocument(document)
        activity = self._convertFromMongo(document)

        for userId in recipientIds:
            self.user_activity_collection.addUserActivity(userId, activity.activity_id)
        
    def removeActivity(self, userId, activityId):
        self.user_activity_collection.removeUserActivity(userId, activityId)
        return self._removeDocument(activityId)

