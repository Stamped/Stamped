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
import logs

from db.mongodb.MongoUserCollection import MongoUserCollection
from db.mongodb.MongoFriendshipCollection import MongoFriendshipCollection
from db.mongodb.MongoCollectionCollection import MongoCollectionCollection
from db.mongodb.MongoEntityCollection import MongoEntityCollection
from db.mongodb.MongoStampCollection import MongoStampCollection

from utils import lazyProperty, LoggingThreadPool

from api.module import APIModule

class Users(APIModule):

    def __init__(self):
        APIModule.__init__(self)

    @lazyProperty
    def _userDB(self):
        return MongoUserCollection()

    @lazyProperty
    def _friendshipDB(self):
        return MongoFriendshipCollection()
    
    @lazyProperty
    def _collectionDB(self):
        return MongoCollectionCollection()

    @lazyProperty
    def _entityDB(self):
    	return MongoEntityCollection()
    
    @lazyProperty
    def _stampDB(self):
        return MongoStampCollection()

    ### PRIVATE

    def getUserFromIdOrScreenName(self, userTiny):
        if not isinstance(userTiny, Schema):
            userTiny = UserTiny().dataImport(userTiny)

        if userTiny.user_id is None and userTiny.screen_name is None:
            raise StampedMissingParametersError("Required field missing (user id or screen name)")

        if userTiny.user_id is not None:
            return self._userDB.getUser(userTiny.user_id)

        return self._userDB.getUserByScreenName(userTiny.screen_name)

    def _getUserStampDistribution(self, userId):
        stampIds    = self._collectionDB.getUserStampIds(userId)
        stamps      = self._stampDB.getStamps(stampIds)
        entityIds   = map(lambda x: x.entity.entity_id, stamps)
        entities    = self._entityDB.getEntityMinis(entityIds)

        categories  = {}
        num_stamps  = len(stampIds)

        for entity in entities:
            category = entity.category
            categories.setdefault(category, 0)
            categories[category] += 1

        result = []
        for k, v in categories.items():
            distribution = CategoryDistribution()
            distribution.category = k
            distribution.count = v
            result.append(distribution)

        return result

    def _enrichUserObjects(self, users, authUserId=None, **kwargs):

        singleUser = False
        if not isinstance(users, list):
            singleUser  = True
            users       = [users]

        # Only enrich "following" field for now
        if authUserId is not None:
            friends = self._friendshipDB.getFriends(authUserId)
            result = []
            for user in users:
                if user.user_id in friends:
                    user.following = True
                else:
                    user.following = False
                result.append(user)
            users = result

        if singleUser:
            return users[0]

        return users


    ### PUBLIC

    def getUser(self, userRequest, authUserId=None):
        user = self.getUserFromIdOrScreenName(userRequest)

        if user.privacy == True:
            if authUserId is None:
                raise StampedViewUserPermissionsError("Insufficient privileges to view user")

            friendship              = Friendship()
            friendship.user_id      = authUserId
            friendship.friend_id    = user.user_id

            if not self._friendshipDB.checkFriendship(friendship):
                raise StampedViewUserPermissionsError("Insufficient privileges to view user")

        if user.stats.num_stamps is not None and user.stats.num_stamps > 0:
            if user.stats.distribution is None or len(user.stats.distribution) == 0:
                distribution = self._getUserStampDistribution(user.user_id)
                user.stats.distribution = distribution
                ### TEMP: This should be async
                self._userDB.updateDistribution(user.user_id, distribution)

        return self._enrichUserObjects(user, authUserId=authUserId)

    def getUsers(self, userIds, screenNames, authUserId):
        ### TODO: Add check for privacy settings

        users = self._userDB.lookupUsers(userIds, screenNames, limit=100)
        return users

        ### TEMP: Sort result based on user request. This should happen client-side.
        usersByUserIds = {}
        usersByScreenNames = {}
        result = []

        for user in users:
            usersByUserIds[user.user_id] = user
            usersByScreenNames[user.screen_name] = user

        if isinstance(userIds, list):
            for userId in userIds:
                try:
                    result.append(usersByUserIds[userId])
                except Exception:
                    pass

        if isinstance(screenNames, list):
            for screenName in screenNames:
                try:
                    result.append(usersByScreenNames[screenName])
                except Exception:
                    pass

        if len(result) != len(users):
            result = users

        return self._enrichUserObjects(result, authUserId=authUserId)

    def getPrivacy(self, userRequest):
        user = self.getUserFromIdOrScreenName(userRequest)

        return (user.privacy == True)

    def findUsersByEmail(self, authUserId, emails):
        ### TODO: Condense with the other "findUsersBy" functions
        ### TODO: Add check for privacy settings?

        users = self._userDB.findUsersByEmail(emails, limit=100)
        return self._enrichUserObjects(users, authUserId=authUserId)

    def findUsersByPhone(self, authUserId, phone):
        ### TODO: Add check for privacy settings?

        users = self._userDB.findUsersByPhone(phone, limit=100)
        return self._enrichUserObjects(users, authUserId=authUserId)

    def findUsersByTwitter(self, authUserId, user_token, user_secret):
        ### TODO: Add check for privacy settings?
        users = []

        # Grab friend list from Facebook API
        users = self._getTwitterFriends(user_token, user_secret)
        return self._enrichUserObjects(users, authUserId=authUserId)

    def findUsersByFacebook(self, authUserId, user_token=None):
        ### TODO: Add check for privacy settings?
        users = []

        # Grab friend list from Facebook API
        users = self._getFacebookFriends(user_token)
        return self._enrichUserObjects(users, authUserId=authUserId)

    def getFacebookFriendData(self, user_token=None, offset=0, limit=30):
        ### TODO: Add check for privacy settings?
        if user_token is None:
            raise StampedThirdPartyInvalidCredentialsError("Connecting to Facebook requires a valid token")

        # Grab friend list from Facebook API
        return self._facebook.getFriendData(user_token, offset, limit)

    def getTwitterFriendData(self, user_token=None, user_secret=None, offset=0, limit=30):
        ### TODO: Add check for privacy settings?
        if user_token is None or user_secret is None:
            raise StampedThirdPartyInvalidCredentialsError("Connecting to Twitter requires a valid token/secret")

        # Grab friend list from Twitter API
        return self._twitter.getFriendData(user_token, user_secret, offset, limit)

    def searchUsers(self, authUserId, query, limit, relationship):
        if limit <= 0 or limit > 20:
            limit = 20

        ### TODO: Add check for privacy settings

        users = self._userDB.searchUsers(authUserId, query, limit, relationship)
        return self._enrichUserObjects(users, authUserId=authUserId)

    def getSuggestedUsers(self, authUserId, limit=None, offset=None):
        suggested = [
            'justinbieber', 
            'ellendegeneres', 
            'ryanseacrest', 
            'nytimes', 
            'time', 
            'nickswisher', 
            'passionpit', 
            'nymag', 
            'mariobatali', 
            'michaelkors', 
            'parislemon', 
            'kevinrose',
            'harvard',
            'barondavis', 
            'urbandaddy', 
            'tconrad', 
            'bostonglobe', 
        ]
        users = self.getUsers(None, suggested, authUserId)
        users.sort(key=lambda x: suggested.index(x.screen_name.lower()))
        return self._enrichUserObjects(users, authUserId=authUserId)
