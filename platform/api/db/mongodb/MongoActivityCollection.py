#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, logs, copy, pymongo

from datetime                           import datetime, timedelta
from utils                              import lazyProperty
from Schemas                            import *

from AActivityDB                        import AActivityDB
from MongoAlertQueueCollection          import MongoAlertQueueCollection
from MongoActivityItemCollection        import MongoActivityItemCollection
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
    def activity_items_collection(self):
        return MongoActivityItemCollection()

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
            'sort'      : 'timestamp.modified',
            'sortOrder' : pymongo.DESCENDING,
        }

        activityIds = self.activity_links_collection.getActivityIdsForUser(userId, **params)
        activity    = self.activity_items_collection.getActivityItems(activityIds, **sort)

        return activity 
    
    def getActivityForUsers(self, userIds, **kwargs):
        params = {
            'since'     : kwargs.pop('since', None),
            'before'    : kwargs.pop('before', None),
            'limit'     : kwargs.pop('limit', 200),
            'sort'      : 'timestamp.modified',
            'sortOrder' : pymongo.DESCENDING,
        }

        activity = self.activity_items_collection.getActivityForUsers(userIds, **params)

        return activity 
    
    def addActivity(self, verb, **kwargs):
        subject         = kwargs.pop('subject', None)
        objects         = kwargs.pop('objects', {})
        benefit         = kwargs.pop('benefit', None)

        sendAlert       = kwargs.pop('sendAlert', True)
        recipientIds    = kwargs.pop('recipientIds', [])
        group           = kwargs.pop('group', False)
        groupRange      = kwargs.pop('groupRange', None)

        now             = datetime.utcnow()
        alerts          = []
        sentTo          = set()

        try:
            objects = objects.value
        except Exception:
            pass

        activityId      = None

        def _buildActivity():
            activity        = Activity()
            activity.verb   = verb
            if subject is not None:
                activity.subjects = [ subject ]
            if len(objects) > 0:
                activity.objects = ActivityObjectIds(objects)
            if benefit is not None:
                activity.benefit = benefit
            activity.timestamp.created  = now
            activity.timestamp.modified = now
            return activity

        # Insert the activity item individually
        if not group:
            activity    = _buildActivity()
            activity    = self.activity_items_collection.addActivityItem(activity)
            activityId  = activity.activity_id

        # Insert the activity item as a group
        else:
            params = {
                'verb'      : verb,
                'objects'   : objects,
            }

            if groupRange is not None:
                # Add time constraint
                params['since'] = datetime.utcnow() - groupRange

            activityIds = self.activity_items_collection.getActivityIds(**params)

            # Look for activity items
            if len(activityIds) > 0:
                if len(activityIds) > 1:
                    logs.warning('WARNING: matched multiple activityIds for verb (%s) & objects (%s)' % (verb, objects))
                
                activityId = activityIds[0]
                self.activity_items_collection.addSubjectToActivityItem(activityId, subject, modified=now)
                if benefit is not None:
                    self.activity_items_collection.setBenefitForActivityItem(activityId, benefit)

            # Insert new item
            else:
                activity    = _buildActivity()
                activity    = self.activity_items_collection.addActivityItem(activity)
                activityId  = activity.activity_id
        
        for recipientId in recipientIds:
            if recipientId in sentTo:
                continue
            
            self.activity_links_collection.addActivityLink(activityId, recipientId)

            sentTo.add(recipientId)

            if sendAlert:
                if not activityId:
                    continue
                
                alert               = Alert()
                alert.recipient_id  = recipientId
                alert.activity_id   = activityId
                alert.user_id       = subject
                alert.genre         = verb
                alert.created       = now
                alerts.append(alert)

        if len(alerts): 
            self.alerts_collection.addAlerts(alerts)

    def _removeActivityIds(self, activityIds):
        self.activity_links_collection.removeActivityLinks(activityIds)
        self.activity_items_collection.removeActivityItems(activityIds)

    def _removeSubject(self, activityIds, subjectId):
        toRemove = self.activity_items_collection.removeSubjectFromActivityItems(activityIds, subjectId)
        self._removeActivityIds(toRemove)

    def removeActivity(self, verb, userId, **kwargs):
        stampId     = kwargs.pop('stampId', None)
        commentId   = kwargs.pop('commentId', None)
        friendId    = kwargs.pop('friendId', None)

        if verb in ['like', 'todo'] and stampId is not None:
            activityIds = self.activity_items_collection.getActivityIds(verb=verb, userId=userId, stampId=stampId)
            self._removeSubject(activityIds, userId)

        if verb in ['follower', 'friend'] and friendId is not None:
            activityIds = self.activity_items_collection.getActivityIds(verb=verb, userId=userId, friendId=friendId)
            self._removeSubject(activityIds, userId)

        if verb in ['comment'] and commentId is not None:
            activityIds = self.activity_items_collection.getActivityIds(verb=verb, userId=userId, commentId=commentId)
            self._removeSubject(activityIds, userId)
    
    def removeActivityForStamp(self, stampId):
        activityIds = self.activity_items_collection.getActivityIds(stampId=stampId)
        self._removeActivityIds(activityIds)
    
    def removeUserActivity(self, userId):
        activityIds = self.activity_items_collection.getActivityIds(userId=userId)
        self._removeSubject(activityIds, userId)

