#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, logs, copy, pymongo

from datetime import datetime
from utils import lazyProperty

from Schemas import *

from AMongoCollection import AMongoCollection
from MongoAlertQueueCollection import MongoAlertQueueCollection
from AActivityDB import AActivityDB

class MongoActivityCollection(AMongoCollection, AActivityDB):
    
    """
    Activity Types:
    * restamp
    * mention
    * comment
    * reply
    * like
    * favorite
    * invite_sent
    * invite_received
    * follower
    """
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='activity', primary_key='activity_id', obj=Activity)
        AActivityDB.__init__(self)

        self._collection.ensure_index([('recipient_id', pymongo.ASCENDING), \
                                        ('timestamp.created', pymongo.DESCENDING)])
        self._collection.ensure_index('user.user_id', unique=False)
        self._collection.ensure_index('link.linked_stamp_id', unique=False)

    ### PUBLIC
    
    @lazyProperty
    def alerts_collection(self):
        return MongoAlertQueueCollection()
    
    def getActivity(self, userId, **kwargs):
        since       = kwargs.pop('since', None)
        before      = kwargs.pop('before', None)
        limit       = kwargs.pop('limit', 20)

        params = {'recipient_id': userId}
        
        if since != None and before != None:
            params['timestamp.created'] = {'$gte': since, '$lte': before}
        elif since != None:
            params['timestamp.created'] = {'$gte': since}
        elif before != None:
            params['timestamp.created'] = {'$lte': before}
        
        documents = self._collection.find(params).sort('timestamp.created', \
            pymongo.DESCENDING).limit(limit)

        activity = []
        for document in documents:
            activity.append(self._convertFromMongo(document))

        return activity
    
    def getActivityItem(self, activityId):
        documentId = self._getObjectIdFromString(activityId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)
    
    def addActivity(self, recipientIds, activityItem, **kwargs):
        sendAlert   = kwargs.pop('sendAlert', True)
        checkExists = kwargs.pop('checkExists', False)

        alerts = []

        for recipientId in recipientIds:
            activityId = None
            activity = activityItem.value
            activity['recipient_id'] = recipientId

            if checkExists:
                try:
                    document = self._collection.find_one({
                        'user.user_id': activity['user']['user_id'],
                        'recipient_id': activity['recipient_id'],
                        'genre': activity['genre'],
                    })
                    if not document:
                        activityId = self._collection.insert_one(activity)
                except:
                    pass
            else:
                activityId = self._collection.insert_one(activity)

            if sendAlert:
                if not activityId:
                    continue

                alert = Alert()
                alert.activity_id   = activityId
                alert.recipient_id  = recipientId
                alert.user_id       = activity['user']['user_id']
                alert.genre         = activity['genre']
                alert.created       = activity['timestamp']['created']
                alerts.append(alert)

        if len(alerts):        
            self.alerts_collection.addAlerts(alerts)

        
    def removeActivity(self, genre, userId, **kwargs):
        stampId     = kwargs.pop('stampId', None)
        recipientId = kwargs.pop('recipientId', None)

        if genre in ['like', 'favorite'] and stampId:
            self._collection.remove({
                'user.user_id': userId,
                'link.linked_stamp_id': stampId,
                'genre': genre
            })

        if genre in ['follower', 'friend'] and recipientId:
            self._collection.remove({
                'user.user_id': userId,
                'recipient_id': recipientId,
                'genre': genre
            })


    def removeActivityForStamp(self, stampId):
        self._collection.remove({'link.linked_stamp_id': stampId})
        
    def removeUserActivity(self, userId):
        self._collection.remove({'user.user_id': userId})



