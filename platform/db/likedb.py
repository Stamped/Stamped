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

from utils import lazyProperty

from db.mongodb.MongoUserLikesCollection import MongoUserLikesCollection
from db.mongodb.MongoUserLikesHistoryCollection import MongoUserLikesHistoryCollection
from db.mongodb.MongoStampLikesCollection import MongoStampLikesCollection

class LikeDB(object):

    @lazyProperty
    def _user_likes_collection(self):
        return MongoUserLikesCollection()

    @lazyProperty
    def _user_likes_history_collection(self):
        return MongoUserLikesHistoryCollection()

    @lazyProperty
    def _stamp_likes_collection(self):
        return MongoStampLikesCollection()


    def add(self, user_id, stamp_id):
        # Add a reference to the user in the stamp's 'like' collection
        self._stamp_likes_collection.addStampLike(stamp_id, user_id) 
        # Add a reference to the stamp in the user's 'like' collection
        self._user_likes_collection.addUserLike(user_id, stamp_id) 
        # Add a reference to the stamp in the user's 'like' history collection
        self._user_likes_history_collection.addUserLike(user_id, stamp_id)

    def remove(self, user_id, stamp_id):
        # Remove a reference to the user in the stamp's 'like' collection
        stamp_like = self._stamp_likes_collection.removeStampLike(stamp_id, user_id)
        # Remove a reference to the stamp in the user's 'like' collection
        user_like = self._user_likes_collection.removeUserLike(user_id, stamp_id)

        if stamp_like == True and user_like == True:
            return True
        return False

    def get(self, stamp_id):
        return self._stamp_likes_collection.getStampLikes(stamp_id)

    def get_for_user(self, user_id):
        return self._user_likes_collection.getUserLikes(user_id)

    def get_history_for_user(self, user_id):
        return self._user_likes_history_collection.getUserLikes(user_id)

    def remove_history_for_user(self, user_id):
        return self._user_likes_history_collection.removeUserLikes(user_id)

    def count(self, stamp_id):
        return len(self.get(stamp_id))

    def count_for_user(self, user_id):
        return len(self.get_for_user(user_id))

    def check(self, user_id, stamp_id):
        likes = self._stamp_likes_collection.getStampLikes(stamp_id)
        if user_id in likes:
            return True
        return False
