#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals

from datetime import datetime
from utils import lazyProperty

from AMongoCollection import AMongoCollection
from MongoUserActivityCollection import MongoUserActivityCollection

from api.AActivityDB import AActivityDB
from api.Activity import Activity

class MongoActivityCollection(AMongoCollection, AActivityDB):
    
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

        documentIds = []
        for activityId in activityIds:
            documentIds.append(self._getObjectIdFromString(activityId))

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




    def addActivityForRestamp(self, recipientIds, user, stamp):
        activity = {}
        activity['genre'] = 'restamp'
        activity['user'] = user.getDataAsDict()
        activity['stamp'] = stamp.getDataAsDict()
        activity = Activity(activity)
        
        activity.timestamp = { 'created': datetime.utcnow() }
        
        if activity.isValid == False:
            raise KeyError("Activity not valid")
        
        activityId = self._addDocument(activity, 'activity_id')
        for userId in recipientIds:
            self.user_activity_collection.addUserActivity(userId, activityId)
            
        return activityId

    def addActivityForComment(self, recipientIds, user, stamp, comment):
        activity = {}
        activity['genre'] = 'comment'
        activity['user'] = user.getDataAsDict()
        activity['stamp'] = stamp.getDataAsDict()
        activity['comment'] = comment.getDataAsDict()
        activity = Activity(activity)
        
        activity.timestamp = { 'created': datetime.utcnow() }
        
        if activity.isValid == False:
            raise KeyError("Activity not valid")
        
        activityId = self._addDocument(activity, 'activity_id')
        for userId in recipientIds:
            self.user_activity_collection.addUserActivity(userId, activityId)
            
        return activityId

    def addActivityForReply(self, recipientIds, user, stamp, comment):
        activity = {}
        activity['genre'] = 'reply'
        activity['user'] = user.getDataAsDict()
        activity['stamp'] = stamp.getDataAsDict()
        activity['comment'] = comment.getDataAsDict()
        activity = Activity(activity)
        
        activity.timestamp = { 'created': datetime.utcnow() }
        
        if activity.isValid == False:
            raise KeyError("Activity not valid")
        
        activityId = self._addDocument(activity, 'activity_id')
        for userId in recipientIds:
            MongoUserActivityCollection().addUserActivity(userId, activityId)
            
        return activityId

    def addActivityForFavorite(self, recipientIds, user, favorite):
        activity = {}
        activity['genre'] = 'favorite'
        activity['user'] = user.getDataAsDict()
        activity['favorite'] = favorite.getDataAsDict()
        activity = Activity(activity)
        
        activity.timestamp = { 'created': datetime.utcnow() }
        
        if activity.isValid == False:
            raise KeyError("Activity not valid")
        
        activityId = self._addDocument(activity, 'activity_id')
        for userId in recipientIds:
            self.user_activity_collection.addUserActivity(userId, activityId)
            
        return activityId

    def addActivityForDirected(self, recipientIds, user, stamp):
        activity = {}
        activity['genre'] = 'directed'
        activity['user'] = user.getDataAsDict()
        activity['stamp'] = stamp.getDataAsDict()
        activity = Activity(activity)
        
        activity.timestamp = { 'created': datetime.utcnow() }
        
        if activity.isValid == False:
            raise KeyError("Activity not valid")
        
        activityId = self._addDocument(activity, 'activity_id')
        for userId in recipientIds:
            self.user_activity_collection.addUserActivity(userId, activityId)
            
        return activityId

    def addActivityForMention(self, recipientIds, user, stamp, comment=None):
        activity = {}
        activity['genre'] = 'mention'
        activity['user'] = user.getDataAsDict()
        activity['stamp'] = stamp.getDataAsDict()
        if comment != None:
            activity['comment'] = comment.getDataAsDict()
        activity = Activity(activity)
        
        activity.timestamp = { 'created': datetime.utcnow() }
        
        if activity.isValid == False:
            raise KeyError("Activity not valid")
        
        activityId = self._addDocument(activity, 'activity_id')
        for userId in recipientIds:
            self.user_activity_collection.addUserActivity(userId, activityId)
            
        return activityId

    def addActivityForMilestone(self, recipientId, milestone):
        raise NotImplementedError
        
    def removeActivity(self, activityId):
        self.user_activity_collection.removeUserActivity(userId, activityId)
        return self._removeDocument(activityId)

