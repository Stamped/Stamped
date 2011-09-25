#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, logs, copy

from datetime import datetime
from utils import lazyProperty

from Schemas import *

from AMongoCollection import AMongoCollection
from MongoUserActivityCollection import MongoUserActivityCollection
from AActivityDB import AActivityDB

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
        AMongoCollection.__init__(self, collection='activity', primary_key='activity_id', obj=Activity)
        AActivityDB.__init__(self)
    
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

        # logs.debug("ACTIVITY IDS: %s" % activityIds)

        documentIds = []
        for activityId in activityIds:
            documentIds.append(self._getObjectIdFromString(activityId))

        # logs.debug("DOCUMENT IDS: %s" % documentIds)

        # Get stamps
        documents = self._getMongoDocumentsFromIds(documentIds, **params)

        activity = []
        for document in documents:
            activity.append(self._convertFromMongo(document))

        return activity
    
    def addActivity(self, recipientIds, activity):
        # activity = self._addObject(activity)
        activity = activity.value
        query = copy.copy(activity)
        query.pop('timestamp')
        # Note: I don't like doing safe=True, but it's necessary to get the _id
        # back. We might want to explore different options here eventually.
        result = self._collection.update(query, activity, upsert=True, safe=True)
        if 'upserted' in result:
            activity_id = self._getStringFromObjectId(result['upserted'])
            if not isinstance(recipientIds, list):
                msg = 'Must pass recipients as list'
                logs.warning(msg)
                raise Exception(msg)
            for userId in recipientIds:
                self.user_activity_collection.addUserActivity(userId, \
                    activity_id)
        
    def removeActivity(self, userId, activityId):
        self.user_activity_collection.removeUserActivity(userId, activityId)
        return self._removeDocument(activityId)

