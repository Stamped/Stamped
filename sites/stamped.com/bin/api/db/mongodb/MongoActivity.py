#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from threading import Lock
from datetime import datetime

from api.AActivityDB import AActivityDB
from api.Activity import Activity
from MongoDB import Mongo
from MongoUserActivity import MongoUserActivity

class MongoActivity(AActivityDB, Mongo):
        
    COLLECTION = 'activity'
        
    SCHEMA = {
        '_id': object,
        'genre': basestring, # comment, reply, restamp, favorite, directed, mention, credit milestone
        'user': {
            'user_id': basestring,
            'screen_name': basestring,
            'display_name': basestring,
            'profile_image': basestring,
            'color_primary': basestring,
            'color_secondary': basestring,
            'privacy': bool
        },
        'comment': {
            'comment_id': basestring,
            'stamp_id': basestring,
            'user': {
                'user_id': basestring,
                'screen_name': basestring,
                'display_name': basestring,
                'profile_image': basestring,
                'color_primary': basestring,
                'color_secondary': basestring,
                'privacy': bool
            },
            'restamp_id': basestring,
            'blurb': basestring,
            'mentions': [],
            'timestamp': {
                'created': datetime
            }
        },
        'stamp': {
            'stamp_id': basestring,
            'entity': {
                'entity_id': basestring,
                'title': basestring,
                'coordinates': {
                    'lat': float, 
                    'lng': float
                },
                'category': basestring,
                'subtitle': basestring
            },
            'user': {
                'user_id': basestring,
                'screen_name': basestring,
                'display_name': basestring,
                'profile_image': basestring,
                'color_primary': basestring,
                'color_secondary': basestring,
                'privacy': bool
            },
            'blurb': basestring,
            'image': basestring,
            'mentions': list,
            'credit': list,
            'comment_preview': list,
            'timestamp': {
                'created': datetime,
                'modified': datetime
            },
            'flags': {
                'flagged': bool,
                'locked': bool
            },
            'stats': {
                'num_comments': int,
                'num_todos': int,
                'num_credit': int
            }
        },
        'favorite': {
            'favorite_id': basestring,
            'entity': {
                'entity_id': basestring,
                'title': basestring,
                'coordinates': {
                    'lat': float, 
                    'lng': float
                },
                'category': basestring,
                'subtitle': basestring
            },
            'user_id': basestring,
            'stamp': {
                'stamp_id': basestring,
                'display_name': basestring,
                'user_id': basestring
            },
            'timestamp': {
                'created': datetime,
                'modified': datetime
            },
        },
        'timestamp': {
            'created': datetime
        }
    }
    
    def __init__(self, setup=False):
        AActivityDB.__init__(self, self.DESC)
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
  
    def addActivity(self, recipientId, activity):
        raise NotImplementedError

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
            MongoUserActivity().addUserActivity(userId, activityId)
            
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
            MongoUserActivity().addUserActivity(userId, activityId)
            
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
            MongoUserActivity().addUserActivity(userId, activityId)
            
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
            MongoUserActivity().addUserActivity(userId, activityId)
            
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
            MongoUserActivity().addUserActivity(userId, activityId)
            
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
            MongoUserActivity().addUserActivity(userId, activityId)
            
        return activityId

    def addActivityForMilestone(self, recipientId, milestone):
        raise NotImplementedError
        
        
    
    def getActivity(self, userId, since=None, before=None, limit=20):

        # Get activity
        activityIds = MongoUserActivity().getUserActivityIds(userId)
        activityData = self._getDocumentsFromIds(
                            activityIds, objId='activity_id', since=since, 
                            before=before, sort='timestamp.created', limit=limit)
        
        # Loop through and validate
        result = []
        for activity in activityData:
            activity = Activity(activity)
            if activity.isValid == False:
                raise KeyError("Activity not valid")
            result.append(activity)
        
        return result
        
    def removeActivity(self, activityId):
        MongoUserActivity().removeUserActivity(userId, activityId)
        return self._removeDocument(activityId)
    
    
    ### PRIVATE
    
