#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from api_old.Schemas import *
from api_old.S3ImageDB import S3ImageDB
from api_old.ActivityCollectionCache import ActivityCollectionCache

import utils
import datetime
import logs

from db.userdb import UserDB
from db.stampdb import StampDB
from db.entitydb import EntityDB
from db.accountdb import AccountDB
from db.commentdb import CommentDB
from db.activitydb import ActivityDB
from db.friendshipdb import FriendshipDB

from api.utils import enrich_stamp_objects

from utils import lazyProperty, LoggingThreadPool

from api.helpers import APIObject

class ActivityAPI(APIObject):

    def __init__(self):
        APIObject.__init__(self)

        self.ACTIVITY_CACHE_BLOCK_SIZE = 50
        self.ACTIVITY_CACHE_BUFFER_SIZE = 20

        self._activityCache = ActivityCollectionCache(self, cacheBlockSize=self.ACTIVITY_CACHE_BLOCK_SIZE, 
            cacheBufferSize=self.ACTIVITY_CACHE_BUFFER_SIZE)


    @lazyProperty
    def _userDB(self):
        return UserDB()
    
    @lazyProperty
    def _stampDB(self):
        return StampeDB()

    @lazyProperty
    def _entityDB(self):
        return EntityDB()
    
    @lazyProperty
    def _commentDB(self):
        return CommentDB()
    
    @lazyProperty
    def _accountDB(self):
        return AccountDB()
    
    @lazyProperty
    def _activityDB(self):
        return ActivityDB()

    @lazyProperty
    def _friendshipDB(self):
        return FriendshipDB()


    def addFollowActivity(self, userId, friendId):
        objects = ActivityObjectIds()
        objects.user_ids = [ friendId ]
        self.addActivity('follow', userId, objects,
                                            group=True,
                                            groupRange=datetime.timedelta(days=1),
                                            unique=True)

    def addCreditActivity(self, userId, recipientIds, stamp_id, benefit):
        objects = ActivityObjectIds()
        objects.user_ids = recipientIds
        objects.stamp_ids = [ stamp_id ]
        self.addActivity('credit', userId, objects,
                                             benefit = benefit)

    def addLikeActivity(self, userId, stampId, friendId, benefit):
        """
        Note: Ideally, if a user "re-likes" a stamp (e.g. they've liked it before and they
        like it again), it should bump the activity item to the top of your feed. There are a 
        whole bunch of pitfalls with this, though. Do you display that the user earned a stamp?
        How is grouping handled, especially if it's grouped previously? What's the upside 
        (especially if the second like is an accident)? 

        Punting for now, but we can readdress after v2 launch.
        """
        objects = ActivityObjectIds()
        objects.stamp_ids = [ stampId ]
        objects.user_ids = [ friendId ]
        self.addActivity('like', userId, objects,
                                          group = True,
                                          groupRange = datetime.timedelta(days=1),
                                          benefit = benefit)

    def addTodoActivity(self, userId, recipientIds, entityId, stampId):
        objects = ActivityObjectIds()
        objects.entity_ids = [ entityId ]
        objects.stamp_ids = [ stampId ]
        self.addActivity('todo', userId, objects,
                                          recipientIds=recipientIds,
                                          requireRecipient=True,
                                          group=True,
                                          groupRange=datetime.timedelta(days=1))

    def addCommentActivity(self, userId, recipientIds, stampId, commentId):
        objects = ActivityObjectIds()
        objects.stamp_ids = [ stampId ]
        objects.comment_ids = [ commentId ]
        self.addActivity('comment', userId, objects,
                                             recipientIds = recipientIds)

    def addReplyActivity(self, userId, recipientIds, stampId, commentId):
        objects = ActivityObjectIds()
        objects.stamp_ids = [ stampId ]
        objects.comment_ids = [ commentId ]
        self.addActivity('reply', userId, objects,
                                           recipientIds = recipientIds,
                                           requireRecipient = True)

    def addMentionActivity(self, userId, recipientIds, stampId=None, commentId=None):
        if stampId is None and commentId is None:
            raise Exception('Mention activity must include either a stampId or commentId')
        objects = ActivityObjectIds()
        if stampId is not None:
            objects.stamp_ids = [ stampId ]
        if commentId is not None:
            objects.comment_ids = [ commentId ]
        validRecipientIds = []
        for recipientId in recipientIds:
            # Check if block exists between user and mentioned user
            friendship              = Friendship()
            friendship.user_id      = recipientId
            friendship.friend_id    = userId
            if self._friendshipDB.blockExists(friendship) == False:
                validRecipientIds.append(recipientId)
        self.addActivity('mention', userId, objects,
                                             recipientIds = validRecipientIds,
                                             requireRecipient = True)

    def addInviteActivity(self, userId, friendId, recipientIds):
        objects = ActivityObjectIds()
        objects.user_ids        = [ friendId ]
        self.addActivity('invite', userId, objects,
                                            recipientIds = recipientIds,
                                            requireRecipient = True,
                                            unique = True)

    def addLinkedFriendActivity(self, userId, service_name, recipientIds, body=None):
        objects = ActivityObjectIds()
        objects.user_ids = [ userId ]
        self.addActivity('friend_%s' % service_name, userId, objects,
                                                              body = body,
                                                              recipientIds = recipientIds,
                                                              requireRecipient = True,
                                                              unique = True)

    def addActionCompleteActivity(self, userId, action_name, source, stampId, friendId, body=None):
        objects = ActivityObjectIds()
        objects.user_ids        = [ friendId ]
        objects.stamp_ids       = [ stampId ]
        self.addActivity('action_%s' % action_name, userId, objects,
                                                             source = source,
                                                             body = body,
                                                             group = True,
                                                             groupRange = datetime.timedelta(days=1),
                                                             unique = True)

    def addWelcomeActivity(self, recipientId):
        objects = ActivityObjectIds()
        objects.user_ids = [ recipientId ]
        body = "We've given you 100 stamps to start, and you earn more if your friends like what you stamp. Try using one now!"
        self._activityDB.addActivity(verb           = 'notification_welcome', 
                                     recipientIds   = [ recipientId ], 
                                     objects        = objects, 
                                     body           = body,
                                     benefit        = 100, 
                                     unique         = True)

    def addFBLoginActivity(self, recipientId):
        objects = ActivityObjectIds()
        objects.user_ids = [ recipientId ]
        body = 'Tap here to share your stamps and activity with friends. You can always change preferences in "Settings."'
        self._activityDB.addActivity(verb           = 'notification_fb_login',
                                     recipientIds   = [ recipientId ],
                                     objects        = objects,
                                     body           = body,
                                     unique         = True)

    def addActivity(self, verb,
                           userId,
                           objects,
                           source=None,
                           body=None,
                           recipientIds=[],
                           requireRecipient=False,
                           benefit=None,
                           group=False,
                           groupRange=None,
                           sendAlert=True,
                           unique=False):

        ### RESTRUCTURE TODO:  Verify that activity is enabled
        # if not self._activity:
        #     return

        if len(recipientIds) == 0 and objects.user_ids is not None and len(objects.user_ids) != 0:
            recipientIds = objects.user_ids

        if userId in recipientIds:
            recipientIds.remove(userId)

        if requireRecipient and len(recipientIds) == 0:
            raise StampedActivityMissingRecipientError("Missing recipient")

        # Save activity
        self._activityDB.addActivity(verb           = verb,
                                     subject        = userId,
                                     objects        = objects,
                                     source         = source,
                                     body           = body,
                                     recipientIds   = recipientIds,
                                     benefit        = benefit,
                                     group          = group,
                                     groupRange     = groupRange,
                                     sendAlert      = sendAlert,
                                     unique         = unique)

        # Increment unread news for all recipients
        if len(recipientIds) > 0:
            self._userDB.updateUserStats(recipientIds, 'num_unread_news', increment=1)

    def getActivity(self, authUserId, scope, limit=20, offset=0):

        activityData, final = self._activityCache.getFromCache(limit, offset, scope=scope, authUserId=authUserId)

        # Append user objects
        userIds     = {}
        stampIds    = {}
        entityIds   = {}
        commentIds  = {}
        for item in activityData:
            if item.subjects is not None:
                for userId in item.subjects:
                    userIds[str(userId)] = None

            if item.objects is not None:
                if item.objects.user_ids is not None:
                    for userId in item.objects.user_ids:
                        userIds[str(userId)] = None

                if item.objects.stamp_ids is not None:
                    for stampId in item.objects.stamp_ids:
                        stampIds[str(stampId)] = None

                if item.objects.entity_ids is not None:
                    for entityId in item.objects.entity_ids:
                        entityIds[str(entityId)] = None

                if item.objects.comment_ids is not None:
                    for commentId in item.objects.comment_ids:
                        commentIds[str(commentId)] = None

        personal = (scope == 'me')

        # Enrich users
        users = self._userDB.lookupUsers(userIds.keys(), None)

        for user in users:
            userIds[str(user.user_id)] = user.minimize()

        # Enrich stamps
        stamps = self._stampDB.getStamps(stampIds.keys())

        stamps = enrich_stamp_objects(stamps, authUserId=authUserId, mini=True)
        for stamp in stamps:
            stampIds[str(stamp.stamp_id)] = stamp

        # Enrich entities
        entities = self._entityDB.getEntityMinis(entityIds.keys())
        for entity in entities:
            entityIds[str(entity.entity_id)] = entity

        # Enrich comments
        comments = self._commentDB.getComments(commentIds.keys())
        commentUserIds = {}
        for comment in comments:
            if comment.user.user_id not in userIds:
                commentUserIds[comment.user.user_id] = None
        users = self._userDB.lookupUsers(commentUserIds.keys(), None)
        for user in users:
            userIds[str(user.user_id)] = user.minimize()
        for comment in comments:
            comment.user = userIds[str(comment.user.user_id)]
            commentIds[str(comment.comment_id)] = comment

        ### TEMP CODE FOR LOCAL COPY THAT DOESN'T ENRICH PROPERLY
        activity = []
        for item in activityData:
            try:
                activity.append(item.enrich(authUserId  = authUserId,
                                            users       = userIds,
                                            stamps      = stampIds,
                                            entities    = entityIds,
                                            comments    = commentIds,
                                            personal    = personal))

            except Exception as e:
                logs.warning('Activity enrichment failed: %s' % e)
                logs.info('Activity item: \n%s\n' % item)
                utils.printException()
                continue

        # Reset activity count
        if personal == True:
            self._accountDB.updateUserTimestamp(authUserId, 'activity', datetime.datetime.utcnow())
            ### DEPRECATED
            self._userDB.updateUserStats(authUserId, 'num_unread_news', value=0)

        return activity

    def getUnreadActivityCount(self, authUserId, **kwargs):
        ### TODO: Cache this in user.num_unread_news
        user = self._userDB.getUser(authUserId)
        count = self._activityDB.getUnreadActivityCount(authUserId, user.timestamp.activity)
        if count is None:
            return 0
        return count
