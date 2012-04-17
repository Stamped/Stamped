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


    
    def addActivity(self, recipientIds, activityObject, **kwargs):
        sendAlert   = kwargs.pop('sendAlert', True)
        checkExists = kwargs.pop('checkExists', False)
        
        alerts = []
        sentTo = set()

        if activityObject.activity_id is None:
            try:
                activityObject = self.activity_objects_collection.matchActivityObject(activityObject)
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


    


    def removeActivity(self, genre, userId, **kwargs):
        return False
        stampId     = kwargs.pop('stampId', None)
        commentId   = kwargs.pop('commentId', None)
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

        if genre in ['comment'] and commentId:
            self._collection.remove({
                'user.user_id': userId,
                'link.linked_comment_id': commentId,
                'genre': genre
            })
    
    def removeActivityForStamp(self, stampId):
        return False
        self._collection.remove({'link.linked_stamp_id': stampId})
    
    def removeUserActivity(self, userId):
        return False
        self._collection.remove({'user.user_id': userId})

