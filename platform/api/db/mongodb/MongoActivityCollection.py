#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, logs, copy, pymongo

from datetime                           import datetime, timedelta
from utils                              import lazyProperty
from api.Schemas                            import *

from AActivityDB                        import AActivityDB
from MongoAlertQueueCollection          import MongoAlertQueueCollection
from MongoActivityItemCollection        import MongoActivityItemCollection
from MongoActivityLinkCollection        import MongoActivityLinkCollection

class MongoActivityCollection(AActivityDB):
    
    """
    Activity Types:
    * credit
    * mention
    * comment
    * reply
    * like
    * todo
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

    def getActivityIdsForUser(self, userId, **kwargs):
        params = {
            'since'     : kwargs.pop('since', None),
            'before'    : kwargs.pop('before', None),
            'limit'     : kwargs.pop('limit', 0),
            'sort'      : 'timestamp.modified',
            'sortOrder' : pymongo.DESCENDING,
            }
        return self.activity_links_collection.getActivityIdsForUser(userId, **params)
    
    def getActivity(self, userId, **kwargs):
        activityIds = self.getActivityIdsForUser(userId, **kwargs)

        kwargs['sort'] = 'timestamp.modified'
        kwargs['sortOrder'] = pymongo.DESCENDING

        activity    = self.activity_items_collection.getActivityItems(activityIds, **kwargs)
        return activity

    def getActivityForUsers(self, userIds, **kwargs):
        params = {
            'verbs'     : kwargs.pop('verbs', []),
            'since'     : kwargs.pop('since', None),
            'before'    : kwargs.pop('before', None),
            'limit'     : kwargs.pop('limit', 200),
            'sort'      : 'timestamp.modified',
            'sortOrder' : pymongo.DESCENDING,
        }

        activity = self.activity_items_collection.getActivityForUsers(userIds, **params)

        return activity

    def getUnreadActivityCount(self, userId, timestamp):
        return self.activity_links_collection.countActivityIdsForUser(userId, since=timestamp)
    
    def addActivity(self, verb, **kwargs):
        subject         = kwargs.pop('subject', None)
        objects         = kwargs.pop('objects', {})
        benefit         = kwargs.pop('benefit', None)
        source          = kwargs.pop('source', None)
        body            = kwargs.pop('body', None)

        sendAlert       = kwargs.pop('sendAlert', True)
        unique          = kwargs.pop('unique', False)   # Check if activity item exists before creating
        recipientIds    = kwargs.pop('recipientIds', [])
        group           = kwargs.pop('group', False)
        groupRange      = kwargs.pop('groupRange', None)

        now             = datetime.utcnow()
        created         = kwargs.pop('created', now) 

        alerts          = []
        sentTo          = set()

        if isinstance(objects, Schema):
            objects = objects.dataExport()

        activityId      = None

        def _buildActivity():
            activity            = Activity()
            activity.verb       = verb
            
            if subject is not None:
                activity.subjects = [ subject ]
            if len(objects) > 0:
                activity.objects = ActivityObjectIds().dataImport(objects)
            if source is not None:
                activity.source = source
            if benefit is not None:
                activity.benefit = benefit
            if body is not None:
                activity.body = body

            timestamp           = BasicTimestamp()
            timestamp.created   = created
            timestamp.modified  = created
            activity.timestamp  = timestamp 

            return activity

        # Insert the activity item individually
        if not group:
            # Short-circuit if the item exists and it's considered unique
            if unique:
                activityIds = self.activity_items_collection.getActivityIds(verb=verb, objects=objects)
                if len(activityIds) > 0:
                    return

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
                params['since'] = created - groupRange

            activityIds = self.activity_items_collection.getActivityIds(**params)

            # Look for activity items
            if len(activityIds) > 0:
                if len(activityIds) > 1:
                    logs.warning('WARNING: matched multiple activityIds for verb (%s) & objects (%s)' % (verb, objects))
                
                activityId = activityIds[0]
                
                # Check if subject already exists
                item = self.activity_items_collection.getActivityItem(activityId)
                if subject not in item.subjects:
                    self.activity_items_collection.addSubjectToActivityItem(activityId, subject, modified=created)
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
            
            self.activity_links_collection.saveActivityLink(activityId, recipientId, created=created)

            sentTo.add(recipientId)

            if sendAlert:
                if not activityId:
                    continue
                
                alert               = Alert()
                alert.activity_id   = activityId
                alert.recipient_id  = recipientId
                alert.subject       = subject
                alert.verb          = verb
                alert.objects       = ActivityObjectIds().dataImport(objects)
                alert.created       = created
                alerts.append(alert)

        if len(alerts): 
            self.alerts_collection.addAlerts(alerts)

    def _removeActivityIds(self, activityIds):
        self.activity_links_collection.removeActivityLinks(activityIds)
        self.activity_items_collection.removeActivityItems(activityIds)

    def _removeSubject(self, activityIds, subjectId):
        toRemove = self.activity_items_collection.removeSubjectFromActivityItems(activityIds, subjectId)
        self._removeActivityIds(toRemove)

    def _removeActivity(self, verb, userId, objects):
        subjects    = [ userId ]
        activityIds = self.activity_items_collection.getActivityIds(verb=verb, subjects=subjects, objects=objects)
        self._removeSubject(activityIds, userId)

    def removeLikeActivity(self, userId, stampId):
        objects = { 'stamp_ids' : [ stampId ] }
        return self._removeActivity('like', userId, objects)

    def removeTodoActivity(self, userId, entityId):
        objects = { 'entity_ids' : [ entityId ] }
        return self._removeActivity('todo', userId, objects)

    def removeFollowActivity(self, userId, friendId):
        objects = { 'user_ids' : [ friendId ] }
        return self._removeActivity('follow', userId, objects)

    def removeFriendActivity(self, userId, friendId):
        objects = { 'user_ids' : [ friendId ] }
        return self._removeActivity('friend', userId, objects)

    def removeCommentActivity(self, userId, commentId):
        objects = { 'comment_ids' : [ commentId ] }
        return self._removeActivity('comment', userId, objects)

    def removeActivityForStamp(self, stampId):
        objects     = { 'stamp_ids' : [ stampId ] }
        activityIds = self.activity_items_collection.getActivityIds(objects=objects)
        self._removeActivityIds(activityIds)
    
    def removeUserActivity(self, userId):
        subjects    = [ userId ]
        activityIds = self.activity_items_collection.getActivityIds(subjects=subjects)
        self._removeSubject(activityIds, userId)

