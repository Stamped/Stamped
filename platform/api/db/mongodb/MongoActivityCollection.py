#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, logs, copy, pymongo

from datetime                           import datetime
from utils                              import lazyProperty
from Schemas                            import *

from AActivityDB                        import AActivityDB
from MongoAlertQueueCollection          import MongoAlertQueueCollection
from MongoActivityObjectCollection      import MongoActivityObjectCollection
from MongoActivityLinkCollection        import MongoActivityLinkCollection

class MongoActivityCollection(AActivityDB):
    
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
        AActivityDB.__init__(self)

    ### PUBLIC
    
    @lazyProperty
    def alerts_collection(self):
        return MongoAlertQueueCollection()

    @lazyProperty
    def activity_objects_collection(self):
        return MongoActivityObjectCollection()

    @lazyProperty
    def activity_links_collection(self):
        return MongoActivityLinkCollection()
    
    def getActivity(self, userId, **kwargs):
        params = {
            'since'     : kwargs.pop('since', None),
            'before'    : kwargs.pop('before', None),
            'limit'     : kwargs.pop('limit', 20),
            'sort'      : 'timestamp.created',
            'sortOrder' : pymongo.DESCENDING,
        }

        sort = {
            'sort'      : 'timestamp.created',
            'sortOrder' : pymongo.DESCENDING,
        }

        activityIds = self.activity_links_collection.getActivityIdsForUser(userId, **params)
        activity    = self.activity_objects_collection.getActivityObjects(activityIds, **sort)

        return activity 
    
    def getActivityForUsers(self, userIds, **kwargs):
        params = {
            'since'     : kwargs.pop('since', None),
            'before'    : kwargs.pop('before', None),
            'limit'     : kwargs.pop('limit', 200),
            'sort'      : 'timestamp.created',
            'sortOrder' : pymongo.DESCENDING,
        }

        activity = self.activity_objects_collection.getActivityForUsers(userIds, **params)

        return activity 
    
    def addActivity(self, recipientIds, activityObject, **kwargs):
        sendAlert   = kwargs.pop('sendAlert', True)
        checkExists = kwargs.pop('checkExists', False)
        
        alerts = []
        sentTo = set()

        if activityObject.activity_id is None:
            try:
                params = {
                    'genre'     : activityObject.genre,
                    'stampId'   : activityObject.stamp_id,
                    'entityId'  : activityObject.entity_id,
                    'userId'    : activityObject.user_id,
                    'friendId'  : activityObject.friend_id,
                    'commentId' : activityObject.comment_id
                }
                activityIds = self.activity_objects_collection.getActivityIds(**params)
                if len(activityIds) == 0:
                    raise Exception

                if len(activityIds) > 1:
                    logs.warning('WARNING: matched multiple activityIds: \n%s' % activityObject)

                activityObject.activity_id = activityIds[0]

            except Exception:
                activityObject = self.activity_objects_collection.addActivityObject(activityObject)
        
        for recipientId in recipientIds:
            if recipientId in sentTo:
                continue
            
            self.activity_links_collection.addActivityLink(activityObject.activity_id, recipientId)

            sentTo.add(recipientId)

            if sendAlert:
                if not activityObject.activity_id:
                    continue
                
                alert               = Alert()
                alert.recipient_id  = recipientId
                alert.activity_id   = activityObject.activity_id
                alert.user_id       = activityObject.user_id
                alert.genre         = activityObject.genre
                alert.created       = activityObject.created
                alerts.append(alert)

        if len(alerts):        
            self.alerts_collection.addAlerts(alerts)

    def _removeActivityIds(self, activityIds):
        self.activity_links_collection.removeActivityLinks(activityIds)
        self.activity_objects_collection.removeActivityObjects(activityIds)

    def removeActivity(self, genre, userId, **kwargs):
        stampId     = kwargs.pop('stampId', None)
        commentId   = kwargs.pop('commentId', None)
        friendId    = kwargs.pop('friendId', None)

        if genre in ['like', 'favorite'] and stampId is not None:
            activityIds = self.activity_objects_collection.getActivityIds(userId=userId, stampId=stampId, genre=genre)
            self._removeActivityIds(activityIds)

        if genre in ['follower', 'friend'] and friendId is not None:
            activityIds = self.activity_objects_collection.getActivityIds(userId=userId, friendId=friendId, genre=genre)
            self._removeActivityIds(activityIds)

        if genre in ['comment'] and commentId is not None:
            activityIds = self.activity_objects_collection.getActivityIds(userId=userId, commentId=commentId, genre=genre)
            self._removeActivityIds(activityIds)
    
    def removeActivityForStamp(self, stampId):
        activityIds = self.activity_objects_collection.getActivityIds(stampId=stampId)
        self._removeActivityIds(activityIds)
    
    def removeUserActivity(self, userId):
        activityIds = self.activity_objects_collection.getActivityIds(userId=userId)
        self._removeActivityIds(activityIds)

