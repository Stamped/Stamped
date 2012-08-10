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

from db.userdb import UserDB
from db.stampdb import StampDB
from db.friendshipdb import FriendshipDB

from db.likedb import LikeDB

from utils import lazyProperty, LoggingThreadPool

from api.helpers import APIObject
from api.stampapi import StampAPI
from api.activityapi import ActivityAPI
from api.entityapi import EntityAPI
from api.accountapi import AccountAPI
from api.linkedaccountapi import LinkedAccountAPI


LIKE_BENEFIT    = 1 # Per like


class LikeAPI(APIObject):

    def __init__(self):
        APIObject.__init__(self)

    @lazyProperty
    def _userDB(self):
        return UserDB()

    @lazyProperty
    def _stampDB(self):
        return StampDB()
    
    @lazyProperty
    def _likeDB(self):
        return LikeDB()
    
    @lazyProperty
    def _friendshipDB(self):
        return FriendshipDB()

    @lazyProperty
    def _stamps(self):
        return StampAPI()

    @lazyProperty
    def _activity(self):
        return ActivityAPI()

    @lazyProperty
    def _entities(self):
        return EntityAPI()

    @lazyProperty
    def _accounts(self):
        return AccountAPI()

    @lazyProperty
    def _linked_account_api(self):
        return LinkedAccountAPI()


    def create(self, auth_user_id, stamp_id):
        stamp = self._stampDB.getStamp(stamp_id)
        stamp = self._stamps.enrichStampObjects(stamp, authUserId=auth_user_id)

        # Check to verify that user hasn't already liked stamp
        if self._likeDB.check(auth_user_id, stamp_id):
            logs.info("'Like' exists for user (%s) on stamp (%s)" % (auth_user_id, stamp_id))
            return stamp

        # Check if user has liked the stamp previously; if so, don't give credit
        previously_liked = False
        history = self._likeDB.get_history_for_user(auth_user_id)
        if stamp_id in history:
            previously_liked = True

        # Add like
        self._likeDB.add(auth_user_id, stamp_id)

        # Force attributes
        if stamp.stats.num_likes is None:
            stamp.stats.num_likes = 0
        stamp.stats.num_likes += 1
        if stamp.attributes is None:
            stamp.attributes = StampAttributesSchema()
        stamp.attributes.is_liked = True

        # Add like async
        payload = {
            'auth_user_id': auth_user_id, 
            'stamp_id': stamp_id, 
            'previously_liked': previously_liked
        }
        self.call_task(self.add_async, payload)

        return stamp

    def addLike(self, authUserId, stampId):
        logs.warning("DEPRECATED FUNCTION: Use 'create' instead")
        return self.create(authUserId, stampId)


    def add_async(self, auth_user_id, stamp_id, previously_liked=False):
        stamp = self._stampDB.getStamp(stamp_id)

        # Increment user stats
        self._userDB.updateUserStats(stamp.user.user_id, 'num_likes', increment=1)
        self._userDB.updateUserStats(auth_user_id, 'num_likes_given', increment=1)

        # Give credit if not previously liked
        if not previously_liked and stamp.user.user_id != auth_user_id:
            # Update user stats with new credit
            self._userDB.updateUserStats(stamp.user.user_id, 'num_stamps_left', increment=LIKE_BENEFIT)

            # Add activity for stamp owner
            self._activity.addLikeActivity(auth_user_id, stamp.stamp_id, stamp.user.user_id, LIKE_BENEFIT)

        # Update entity stats
        self.call_task(self._entities.updateEntityStatsAsync, {'entityId': stamp.entity.entity_id})

        # Update stamp stats
        self.call_task(self._stamps.updateStampStatsAsync, {'stampId': stamp.stamp_id})

        # Post to Facebook Open Graph if enabled
        share_settings = self._accounts.getOpenGraphShareSettings(auth_user_id)
        if share_settings is not None and share_settings.share_likes:
            payload = {'auth_user_id': auth_user_id, 'like_stamp_id': stamp.stamp_id}
            self.call_task(self._linked_account_api.post_og_async, payload)

    def addLikeAsync(self, authUserId, stampId, previouslyLiked=False):
        logs.warning("DEPRECATED: Use 'add_async'")
        return self.add_async(authUserId, stampId, previouslyLiked)


    def remove(self, auth_user_id, stamp_id):
        # Remove like (if it exists)
        if not self._likeDB.remove(auth_user_id, stamp_id):
            logs.info('Like does not exist')
            stamp = self._stampDB.getStamp(stamp_id)
            return self._stamps.enrichStampObjects(stamp, authUserId=auth_user_id)

        # Get stamp object
        stamp = self._stampDB.getStamp(stamp_id)
        stamp = self._stamps.enrichStampObjects(stamp, authUserId=auth_user_id)

        # Decrement user stats by one
        self._userDB.updateUserStats(stamp.user.user_id, 'num_likes',    increment=-1)
        self._userDB.updateUserStats(auth_user_id, 'num_likes_given', increment=-1)

        if stamp.stats.num_likes is None:
            stamp.stats.num_likes = 0

        if stamp.stats.num_likes > 0:
            stamp.stats.num_likes -= 1
        else:
            stamp.stats.num_likes  = 0

        # Update stamp stats
        self.call_task(self._stamps.updateStampStatsAsync, {'stampId': stamp.stamp_id})

        return stamp

    def removeLike(self, authUserId, stampId):
        logs.warning("DEPRECATED: Use 'remove'")
        return self.remove(authUserId, stampId)


    def get(self, stamp_id, auth_user_id):
        ### TODO: Add paging
        stamp = self._stampDB.getStamp(stamp_id)
        
        # Get user ids
        user_ids = self._likeDB.get(stamp_id)
        
        return user_ids

    def getLikes(self, authUserId, stampId):
        logs.warning("DEPRECATED: Use 'get'")
        return self.get(stampId, authuserId)
