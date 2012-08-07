#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, logs, copy, pymongo
import time

from datetime                                           import datetime, timedelta
from utils                                              import lazyProperty
from api.Schemas                                        import *
from pymongo.errors                                     import DuplicateKeyError

from api.AActivityDB                                    import AActivityDB
from api.db.mongodb.AMongoCollection                    import AMongoCollection
from api.db.mongodb.MongoAlertQueueCollection           import MongoAlertQueueCollection
from api.db.mongodb.MongoActivityItemCollection         import MongoActivityItemCollection
from api.db.mongodb.MongoActivityLinkCollection         import MongoActivityLinkCollection
from api.db.mongodb.MongoFriendsCollection              import MongoFriendsCollection


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
        try:
            self.add_raw_activity(verb, **kwargs)
        except Exception as e:
            logs.warning("Failed to run add_raw_activity: %s" % e)

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


        # Individual activity items
        if not group:
            # Short-circuit if the item exists and it's considered unique
            if unique:
                activityIds = self.activity_items_collection.getActivityIds(verb=verb, objects=objects)
                if len(activityIds) > 0:
                    return

            activity    = _buildActivity()
            activity    = self.activity_items_collection.addActivityItem(activity)
            activityId  = activity.activity_id

        # Grouped activity items
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
                
                # Short circuit if subject already exists
                item = self.activity_items_collection.getActivityItem(activityId)
                if subject in item.subjects:
                    return

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
        try:
            self.remove_like_raw_activity(userId, stampId)
        except Exception as e:
            logs.warning(e)

        objects = { 'stamp_ids' : [ stampId ] }
        return self._removeActivity('like', userId, objects)

    def removeTodoActivity(self, userId, entityId):
        try:
            self.remove_todo_raw_activity(userId, entityId)
        except Exception as e:
            logs.warning(e)
            
        objects = { 'entity_ids' : [ entityId ] }
        return self._removeActivity('todo', userId, objects)

    def removeFollowActivity(self, userId, friendId):
        try:
            self.remove_follow_raw_activity(userId, friendId)
        except Exception as e:
            logs.warning(e)
            
        objects = { 'user_ids' : [ friendId ] }
        return self._removeActivity('follow', userId, objects)

    def removeFriendActivity(self, userId, friendId):
        try:
            self.remove_friend_raw_activity(userId, friendId)
        except Exception as e:
            logs.warning(e)
            
        objects = { 'user_ids' : [ friendId ] }
        return self._removeActivity('friend', userId, objects)

    def removeCommentActivity(self, userId, commentId):
        try:
            self.remove_comment_raw_activity(userId, commentId)
        except Exception as e:
            logs.warning(e)
            
        objects = { 'comment_ids' : [ commentId ] }
        return self._removeActivity('comment', userId, objects)

    def removeActivityForStamp(self, stampId):
        try:
            self.remove_raw_activity_for_stamp(stampId)
        except Exception as e:
            logs.warning(e)
            
        objects     = { 'stamp_ids' : [ stampId ] }
        activityIds = self.activity_items_collection.getActivityIds(objects=objects)
        self._removeActivityIds(activityIds)
    
    def removeUserActivity(self, userId):
        try:
            self.remove_user_raw_activity(userId)
        except Exception as e:
            logs.warning(e)
            
        subjects    = [ userId ]
        activityIds = self.activity_items_collection.getActivityIds(subjects=subjects)
        self._removeSubject(activityIds, userId)







    @lazyProperty
    def raw_activity_items_collection(self):
        return MongoRawActivityItemCollection()

    @lazyProperty
    def raw_activity_links_collection(self):
        return MongoRawActivityLinkCollection()

    @lazyProperty
    def friends_collection(self):
        return MongoFriendsCollection()

    def add_raw_activity(self, verb, **kwargs):
        subject         = kwargs.get('subject', None)
        objects         = kwargs.get('objects', {})
        benefit         = kwargs.get('benefit', None)
        source          = kwargs.get('source', None)
        body            = kwargs.get('body', None)

        send_alert      = kwargs.get('sendAlert', True)
        recipient_ids   = kwargs.get('recipientIds', [])

        now             = datetime.utcnow()
        created         = kwargs.get('created', now) 

        if isinstance(objects, Schema):
            objects = objects.dataExport()

        # Build raw activity item
        item = RawActivity()

        item.verb = verb
        item.subject = subject

        ### TODO (PHASE II): Better handling of schema conversion
        obj = RawActivityObjectId()
        if 'user_ids' in objects and len(objects['user_ids']) > 0:
            obj.user_id = objects['user_ids'][0]
        if 'stamp_ids' in objects and len(objects['stamp_ids']) > 0:
            obj.stamp_id = objects['stamp_ids'][0]
        if 'entity_ids' in objects and len(objects['entity_ids']) > 0:
            obj.entity_id = objects['entity_ids'][0]
        if 'comment_ids' in objects and len(objects['comment_ids']) > 0:
            obj.comment_id = objects['comment_ids'][0]
        item.objects = obj

        if source is not None:
            item.source = source

        if benefit is not None:
            item.benefit = benefit

        if body is not None:
            item.body = body

        timestamp = BasicTimestamp()
        timestamp.created = created
        item.timestamp = timestamp 

        # Check if it already exists and insert
        try:
            # Unique index on verb + subject + objects
            activity = self.raw_activity_items_collection.add_activity_item(item)
            activity_id = activity.activity_id
        except DuplicateKeyError as e:
            return

        # Add link
        for recipient_id in recipient_ids:
            self.raw_activity_links_collection.add_activity_link(activity_id, recipient_id, created=created)

            # self.build_activity(recipient_id)
        ### TODO: Create / save alert


    def _remove_raw_activity_ids(self, activity_ids):
        self.raw_activity_links_collection.remove_activity_links(activity_ids)
        self.raw_activity_items_collection.remove_activity_items(activity_ids)

    def _remove_raw_activity(self, verb, user_id, objects):
        activity_ids = self.raw_activity_items_collection.get_activity_ids(verb=verb, subject=user_id, objects=objects)
        self._remove_raw_activity_ids(activity_ids)

    def remove_like_raw_activity(self, user_id, stamp_id):
        return self._remove_raw_activity('like', user_id, objects={'stamp_id': stamp_id})

    def remove_todo_raw_activity(self, user_id, entity_id):
        return self._remove_raw_activity('todo', user_id, objects={'entity_id': entity_id})

    def remove_follow_raw_activity(self, user_id, friend_id):
        return self._remove_raw_activity('follow', user_id, objects={'user_id': friend_id})

    def remove_friend_raw_activity(self, user_id, friend_id):
        return self._remove_raw_activity('friend', user_id, objects={'user_id': friend_id})

    def remove_comment_raw_activity(self, user_id, comment_id):
        return self._remove_raw_activity('comment', user_id, objects={'comment_id': comment_id})

    def remove_raw_activity_for_stamp(self, stamp_id):
        activity_ids = self.raw_activity_items_collection.get_activity_ids(objects={'stamp_id': stamp_id})
        self._remove_raw_activity_ids(activity_ids)
    
    def remove_user_raw_activity(self, user_id):
        activity_ids = self.raw_activity_links_collection.get_activity_ids(subject=user_id)
        self._remove_raw_activity_ids(activity_ids)





    def build_activity(self, user_id):
        """
        Generate cached and grouped activity items for personal and universal news.

        Args
            user_id: the user id keyed to the activity

        Returns: N/A

        """
        activity_ids = self.raw_activity_links_collection.get_activity_ids_for_user(user_id)
        friend_ids = self.friends_collection.getFriends(user_id, limit=None)

        personal_items = self.raw_activity_items_collection.get_activity_items(activity_ids)

        universal_verbs = ['todo', 'follow', 'like', 'comment']
        universal_items = self.raw_activity_items_collection.get_activity_for_users(friend_ids, verbs=universal_verbs)

        def build_activity_keys(items):
            keys = {}
            keys_order = []
            for item in items:
                # Generate unique key
                key = '%s::%s' % (item.verb, item.activity_id)

                # Generate grouped key
                if item.verb == 'todo':
                    key = 'todo::%s::%s' % (item.objects.entity_id, item.timestamp.created.isoformat()[:10])
                    
                elif item.verb == 'follow':
                    key = 'follow::%s::%s' % (item.objects.user_id, item.timestamp.created.isoformat()[:10])

                elif item.verb == 'like' or item.verb == 'credit' or item.verb.startswith('action_'):
                    key = '%s::%s::%s' % (item.verb, item.objects.stamp_id, item.timestamp.created.isoformat()[:10])

                elif item.verb in set(['comment', 'reply', 'mention']):
                    if item.objects.comment_id is not None:
                        key = 'comment::%s' % item.objects.comment_id
                    else:
                        key = 'mention::%s' % item.objects.stamp_id

                # Apply keys
                if key in keys:
                    # Existing item
                    if item.subject is not None and item.subject not in keys[key].subjects:
                        keys[key].subjects = list(keys[key].subjects) + [item.subject]
                        if item.benefit is not None:
                            if keys[key].benefit is None:
                                keys[key].benefit = 0
                            keys[key].benefit += 1
                        if item.timestamp.created > keys[key].timestamp.created:
                            keys[key].timestamp.created = item.timestamp.created
                    else:
                        logs.warning("Missing subjects! %s" % item)
                else:
                    # New item
                    ### TODO (PHASE II): Better handling of schema conversion
                    activity = Activity()
                    activity.benefit = item.benefit
                    activity.timestamp = item.timestamp
                    if item.subject is not None:
                        activity.subjects = [item.subject]
                    activity.verb = item.verb
                    objects = ActivityObjectIds()
                    if item.objects.user_id is not None:
                        objects.user_ids = [item.objects.user_id]
                    if item.objects.stamp_id is not None:
                        objects.stamp_ids = [item.objects.stamp_id]
                    if item.objects.entity_id is not None:
                        objects.entity_ids = [item.objects.entity_id]
                    if item.objects.comment_id is not None:
                        objects.comment_ids = [item.objects.comment_id]
                    activity.objects = objects 
                    activity.source = item.source
                    if item.header is not None:
                        activity.header = item.header
                    if item.body is not None:
                        activity.body = item.body
                    if item.footer is not None:
                        activity.footer = item.footer

                    keys[key] = activity 
                    keys_order.append(key)

            return keys, keys_order

        personal_keys, personal_keys_order = build_activity_keys(personal_items)
        universal_keys, universal_keys_order = build_activity_keys(universal_items)

        mark = str(int(time.time() * 1000000))

        """
        Generate a "sort" value that will be used in the db to order our grouped, cached items. This is composed
        of a timestamp for versioning concatenated with an value for ordering within that timestamp. Queries to the 
        database will return data sorted by this value in descending order, and we can include a check in retrieval 
        to verify that the timestamp is unique -- this is hack to get around the fact that Mongo does not allow 
        for atomic insertion and deletion. 

        It's theoretically possible for two sets of data to have the same timestamp, so we should add an additional 
        hash to decrease the odds of duplication. I'm not terrible concerned about this in the short term, though.

        Also, note that we've effectively capped the number of grouped, cached items that we can generate at 10,000.
        """

        i = 9999
        personal_result = []
        for key in personal_keys_order:
            item = personal_keys[key]
            sort = ("%s|%04d" % (mark, i)).zfill(22)
            personal_result.append((item, sort))
            i -= 1

        i = 9999
        universal_result = []
        for key in universal_keys_order:
            if key not in personal_keys:
                item = universal_keys[key]
                sort = ("%s|%04d" % (mark, i)).zfill(22)
                universal_result.append((item, sort))
                i -= 1



class MongoRawActivityItemCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='rawactivityitems', 
                                        primary_key='activity_id', 
                                        obj=RawActivity, 
                                        overflow=True)

        self._collection.ensure_index('timestamp.modified')

        self._collection.ensure_index([ ('verb', pymongo.ASCENDING), 
                                        ('subject', pymongo.ASCENDING), 
                                        ('objects.user_id', pymongo.ASCENDING), 
                                        ('objects.stamp_id', pymongo.ASCENDING), 
                                        ('objects.entity_id', pymongo.ASCENDING), 
                                        ('objects.comment_id', pymongo.ASCENDING) ], unique=True)

    
    ### PUBLIC
    
    def add_activity_item(self, activity):
        try:
            return self._addObject(activity)
        except DuplicateKeyError:
            logs.info("Activity item already exists: %s" % activity)
            raise
    
    def remove_activity_item(self, activity_id):
        document_id = self._getObjectIdFromString(activity_id)
        result = self._removeMongoDocument(document_id)
        return result
    
    def remove_activity_items(self, activity_ids):
        document_ids = map(self._getObjectIdFromString, activity_ids)
        result = self._removeMongoDocuments(document_ids)
        return result

    def get_activity_item(self, activity_id):
        document_id = self._getObjectIdFromString(activity_id)
        document = self._getMongoDocumentFromId(document_id)
        return self._convertFromMongo(document)

    def get_activity_items(self, activity_ids, **kwargs):
        ids = map(self._getObjectIdFromString, activity_ids)

        documents = self._getMongoDocumentsFromIds(ids, **kwargs)

        return map(self._convertFromMongo, documents)

    def get_activity_ids(self, **kwargs):
        query = {}

        # Subject
        if 'subject' in kwargs:
            query['subject'] = kwargs['subject']

        # Verb
        if 'verb' in kwargs:
            query['verb'] = kwargs['verb']

        # Objects
        if 'objects' in kwargs:
            for k, v in kwargs['objects'].iteritems():
                query['objects.%s' % k] = v

        # Sources
        if 'source' in kwargs:
            query['source'] = kwargs['source']

        # Timestamp
        if 'since' in kwargs:
            query['timestamp.created'] = { '$gte' : kwargs['since'] }

        if len(query.keys()) == 0:
            raise Exception("No params provided!")

        documents = self._collection.find(query, fields={'_id' : 1})

        result = []
        for document in documents:
            result.append(self._getStringFromObjectId(document['_id']))
        return result

    def get_activity_for_users(self, user_ids, **kwargs):
        if len(user_ids) == 0:
            return []
        
        query       = { 'subjects' : { '$in' : user_ids } }

        verbs       = kwargs.pop('verbs', [])
        since       = kwargs.pop('since', None)
        before      = kwargs.pop('before', None)
        limit       = kwargs.pop('limit', 20)

        if len(verbs) > 0:
            query['verb'] = { '$in' : verbs }

        if since is not None and before is not None:
            query['timestamp.created'] = { '$gte' : since, '$lte' : before }
        elif since is not None:
            query['timestamp.created'] = { '$gte' : since }
        elif before is not None:
            query['timestamp.created'] = { '$lte' : before }

        documents = self._collection.find(query).sort('timestamp.created', pymongo.DESCENDING).limit(limit)

        return map(self._convertFromMongo, documents)




class MongoRawActivityLinkCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='rawactivitylinks',
                                        primary_key='link_id', 
                                        obj=ActivityLink, 
                                        overflow=True)

        self._collection.ensure_index([ ('user_id', pymongo.ASCENDING), 
                                        ('timestamp.created', pymongo.DESCENDING) ])

        self._collection.ensure_index([ ('activity_id', pymongo.ASCENDING),
                                        ('user_id', pymongo.ASCENDING)])
    
    ### PUBLIC

    def add_activity_link(self, activity_id, user_id, **kwargs):
        # Note: 'created' was necessary for backfilling data 
        item                = ActivityLink()
        item.activity_id    = activity_id 
        item.user_id        = user_id
        timestamp           = BasicTimestamp()
        timestamp.created   = kwargs.pop('created', datetime.utcnow())
        item.timestamp      = timestamp
        self._addObject(item)

    def remove_activity_link(self, activity_id):
        try:
            self._collection.remove({'activity_id': activity_id})
            return True
        except Exception as e:
            logs.warning("Cannot remove document: %s" % e)
            raise 

    def remove_activity_links(self, activity_ids):
        try:
            self._collection.remove({'activity_id': {'$in': activity_ids}},)
            return True
        except Exception as e:
            logs.warning("Cannot remove documents: %s" % e)
            raise 

    def remove_activity_link_for_user(self, activity_id, user_id):
        try:
            self._collection.remove({'activity_id': activity_id}, {'user_id': user_id})
            return True
        except Exception as e:
            logs.warning("Cannot remove document: %s" % e)
            raise 

    def get_activity_ids_for_user(self, user_id, **kwargs):
        since       = kwargs.pop('since', None)
        before      = kwargs.pop('before', None)
        limit       = kwargs.pop('limit', 0)

        query = { 'user_id' : user_id }
        if since is not None and before is not None:
            query['timestamp.created'] = {'$gte': since, '$lte': before}
        elif since is not None:
            query['timestamp.created'] = {'$gte': since}
        elif before is not None:
            query['timestamp.created'] = {'$lte': before}

        documents = self._collection.find(query).sort('timestamp.created', pymongo.DESCENDING).limit(limit)

        return [ document['activity_id'] for document in documents ]

    def count_activity_ids_for_user(self, user_id, **kwargs):
        since       = kwargs.pop('since', None)
        before      = kwargs.pop('before', None)

        query = { 'user_id' : user_id }
        if since is not None and before is not None:
            query['timestamp.created'] = {'$gte': since, '$lte': before}
        elif since is not None:
            query['timestamp.created'] = {'$gte': since}
        elif before is not None:
            query['timestamp.created'] = {'$lte': before}

        return self._collection.find(query).count()
        

