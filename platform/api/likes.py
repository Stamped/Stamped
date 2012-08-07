#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from api_old.Schemas import *

import utils
import datetime
import time
import logs

from db.mongodb.MongoUserCollection import MongoUserCollection
from db.mongodb.MongoStampCollection import MongoStampCollection
from db.mongodb.MongoFriendshipCollection import MongoFriendshipCollection

from utils import lazyProperty, LoggingThreadPool

from api.module import APIModule
from api.stamps import Stamps
from api.activity import Activity
from api.entities import Entities
from api.accounts import Accounts


LIKE_BENEFIT    = 1 # Per like


class Likes(APIModule):

    def __init__(self):
        APIModule.__init__(self)

    @lazyProperty
    def _userDB(self):
        return MongoUserCollection()
    
    @lazyProperty
    def _stampDB(self):
        return MongoStampCollection()
    
    @lazyProperty
    def _friendshipDB(self):
        return MongoFriendshipCollection()

    @lazyProperty
    def _stamps(self):
        return Stamps()

    @lazyProperty
    def _activity(self):
        return Activity()

    @lazyProperty
    def _entities(self):
        return Entities()

    @lazyProperty
    def _accounts(self):
        return Accounts()


    def addLike(self, authUserId, stampId):
        stamp = self._stampDB.getStamp(stampId)
        stamp = self._stamps.enrichStampObjects(stamp, authUserId=authUserId)

        # Check to verify that user hasn't already liked stamp
        if self._stampDB.checkLike(authUserId, stampId):
            logs.info("'Like' exists for user (%s) on stamp (%s)" % (authUserId, stampId))
            return stamp

        # Check if user has liked the stamp previously; if so, don't give credit
        previouslyLiked = False
        history = self._stampDB.getUserLikesHistory(authUserId)
        if stampId in history:
            previouslyLiked = True

        # Add like
        self._stampDB.addLike(authUserId, stampId)

        # Force attributes
        if stamp.stats.num_likes is None:
            stamp.stats.num_likes = 0
        stamp.stats.num_likes += 1
        if stamp.attributes is None:
            stamp.attributes = StampAttributesSchema()
        stamp.attributes.is_liked = True

        # Add like async
        payload = {
            'authUserId': authUserId, 
            'stampId': stampId, 
            'previouslyLiked': previouslyLiked
        }
        self.call_task(self.addLikeAsync, payload)

        return stamp

    def addLikeAsync(self, authUserId, stampId, previouslyLiked=False):
        stamp = self._stampDB.getStamp(stampId)

        # Increment user stats
        self._userDB.updateUserStats(stamp.user.user_id, 'num_likes', increment=1)
        self._userDB.updateUserStats(authUserId, 'num_likes_given', increment=1)

        # Give credit if not previously liked
        if not previouslyLiked and stamp.user.user_id != authUserId:
            # Update user stats with new credit
            self._userDB.updateUserStats(stamp.user.user_id, 'num_stamps_left', increment=LIKE_BENEFIT)

            # Add activity for stamp owner
            self._activity.addLikeActivity(authUserId, stamp.stamp_id, stamp.user.user_id, LIKE_BENEFIT)

        # Update entity stats
        self.call_task(self._entities.updateEntityStatsAsync, {'entityId': stamp.entity.entity_id})

        # Update stamp stats
        self.call_task(self._stamps.updateStampStatsAsync, {'stampId': stamp.stamp_id})

        # Post to Facebook Open Graph if enabled
        share_settings = self._accounts.getOpenGraphShareSettings(authUserId)
        if share_settings is not None and share_settings.share_likes:
            self.call_task(self.postToOpenGraphAsync, {'authUserId': authUserId, 'likeStampId': stamp.stamp_id})

    def removeLike(self, authUserId, stampId):
        # Remove like (if it exists)
        if not self._stampDB.removeLike(authUserId, stampId):
            logs.warning('Attempted to remove a like that does not exist')
            stamp = self._stampDB.getStamp(stampId)
            return self._stamps.enrichStampObjects(stamp, authUserId=authUserId)

        # Get stamp object
        stamp = self._stampDB.getStamp(stampId)
        stamp = self._stamps.enrichStampObjects(stamp, authUserId=authUserId)

        # Decrement user stats by one
        self._userDB.updateUserStats(stamp.user.user_id, 'num_likes',    increment=-1)
        self._userDB.updateUserStats(authUserId, 'num_likes_given', increment=-1)

        if stamp.stats.num_likes is None:
            stamp.stats.num_likes = 0

        if stamp.stats.num_likes > 0:
            stamp.stats.num_likes -= 1
        else:
            stamp.stats.num_likes  = 0

        # Update stamp stats
        self.call_task(self._stamps.updateStampStatsAsync, {'stampId': stamp.stamp_id})

        return stamp

    def getLikes(self, authUserId, stampId):
        ### TODO: Add paging
        stamp = self._stampDB.getStamp(stampId)
        stamp = self._stamps.enrichStampObjects(stamp, authUserId=authUserId)

        # Verify user has the ability to view the stamp's likes
        if stamp.user.user_id != authUserId:
            friendship              = Friendship()
            friendship.user_id      = stamp.user.user_id
            friendship.friend_id    = authUserId
            
            # Check if stamp is private; if so, must be a follower
            if stamp.user.privacy == True:
                if not self._friendshipDB.checkFriendship(friendship):
                    raise StampedAddCommentPermissionsError("Insufficient privileges to add comment")
            
            if authUserId is not None:
                # Check if block exists between user and stamp owner
                if self._friendshipDB.blockExists(friendship) == True:
                    raise StampedBlockedUserError("Block exists")
        
        # Get user ids
        userIds = self._stampDB.getStampLikes(stampId)
        
        return userIds