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

from db.mongodb.MongoFriendshipCollection import MongoFriendshipCollection
from db.mongodb.MongoAccountCollection import MongoAccountCollection
from db.mongodb.MongoActivityCollection import MongoActivityCollection
from db.mongodb.MongoCollectionCollection import MongoCollectionCollection
from db.mongodb.MongoInvitationCollection import MongoInvitationCollection
from db.mongodb.MongoStampCollection import MongoStampCollection
from db.mongodb.MongoUserCollection import MongoUserCollection

from api.users import Users
from api.activity import Activity
from api.guides import Guides

from utils import lazyProperty, LoggingThreadPool

from api.module import APIObject
from api.accounts import Accounts
from api.linkedaccountapi import LinkedAccountAPI

class Friendships(APIObject):

    def __init__(self):
        APIObject.__init__(self)

    @lazyProperty
    def _friendshipDB(self):
        return MongoFriendshipCollection()

    @lazyProperty
    def _accountDB(self):
        return MongoAccountCollection()
    
    @lazyProperty
    def _activityDB(self):
        return MongoActivityCollection()
    
    @lazyProperty
    def _collectionDB(self):
        return MongoCollectionCollection()
    
    @lazyProperty
    def _inviteDB(self):
        return MongoInvitationCollection()
    
    @lazyProperty
    def _stampDB(self):
        return MongoStampCollection()
    
    @lazyProperty
    def _userDB(self):
        return MongoUserCollection()

    @lazyProperty
    def _users(self):
        return Users()

    @lazyProperty
    def _activity(self):
        return Activity()

    @lazyProperty
    def _guides(self):
        return Guides()

    @lazyProperty
    def _accounts(self):
        return Accounts()

    @lazyProperty
    def _linked_account_api(self):
        return LinkedAccountAPI()


    def addFriendship(self, authUserId, userRequest):
        user = self._users.getUserFromIdOrScreenName(userRequest)

        # Verify that you're not following yourself :)
        if user.user_id == authUserId:
            raise StampedInvalidFriendshipError("Illegal friendship: you can't follow yourself!")

        friendship              = Friendship()
        friendship.user_id      = authUserId
        friendship.friend_id    = user.user_id

        # Check if friendship already exists
        if self._friendshipDB.checkFriendship(friendship) == True:
            logs.info("Friendship exists")
            return user

        # Check if block exists between authenticating user and user
        if self._friendshipDB.blockExists(friendship) == True:
            raise StampedBlockedUserError("Block exists")

        # Check if friend has private account
        if user.privacy == True:
            ### TODO: Create queue for friendship requests
            raise NotImplementedError

        # Create friendship
        self._friendshipDB.addFriendship(friendship)

        # Asynchronously add stamps and activity for newly created friendship
        payload = {
            'authUserId': authUserId,
            'userId': user.user_id,
        }
        self.call_task(self.addFriendshipAsync, payload)

        return user

    def addFriendshipAsync(self, authUserId, userId):
        # Add activity for followed user
        self._activity.addFollowActivity(authUserId, userId)

        # Remove 'friend' activity item
        self._activityDB.removeFriendActivity(authUserId, userId)

        # Add stamps to Inbox
        stampIds = self._collectionDB.getUserStampIds(userId)
        self._stampDB.addInboxStampReferencesForUser(authUserId, stampIds)

        # Increment stats for both users
        self._userDB.updateUserStats(authUserId, 'num_friends',   increment=1)
        self._userDB.updateUserStats(userId,     'num_followers', increment=1)

        # Refresh guide
        self.call_task(self._guides.buildGuideAsync, {'authUserId': authUserId})

        # Post to Facebook Open Graph if enabled
        share_settings = self._accounts.getOpenGraphShareSettings(authUserId)
        if share_settings is not None and share_settings.share_follows:
            friendAcct = self.getAccount(userId)

            # We need to check two things: 1) The friend has a linked FB account
            #                              2) We have the friend's FB 'third_party_id'.  If not, we'll get it
            if friendAcct.linked is not None and friendAcct.linked.facebook is not None and \
               friendAcct.linked.facebook.linked_user_id is not None:
                # If the friend has an FB linked account but we don't have the third_party_id, get it
                if friendAcct.linked.facebook.third_party_id is None:
                    friend_fb_id = friendAcct.linked.facebook.linked_user_id
                    acct = self.getAccount(authUserId)
                    token = acct.linked.facebook.token
                    friend_info = self._facebook.getUserInfo(token, friend_fb_id)
                    friend_linked = friendAcct.linked.facebook
                    friend_linked.third_party_id = friend_info['third_party_id']
                    self._accountDB.updateLinkedAccount(userId, friend_linked)
                payload = {
                    'auth_user_id': authUserId,
                    'follow_user_id': userId,
                }
                self.call_task(self._linked_account_api.post_og_async, payload)

    def removeFriendship(self, authUserId, userRequest):
        user                    = self._users.getUserFromIdOrScreenName(userRequest)
        friendship              = Friendship()
        friendship.user_id      = authUserId
        friendship.friend_id    = user.user_id

        # Check if friendship doesn't exist
        if self._friendshipDB.checkFriendship(friendship) == False:
            logs.info("Friendship does not exist")
            return user

        self._friendshipDB.removeFriendship(friendship)

        # Asynchronously remove stamps for this friendship
        payload = {
            'authUserId': authUserId,
            'userId': user.user_id,
        }
        self.call_task(self.removeFriendshipAsync, payload)

        return user

    def removeFriendshipAsync(self, authUserId, userId):
        # Decrement stats for both users
        self._userDB.updateUserStats(authUserId, 'num_friends',   increment=-1)
        self._userDB.updateUserStats(userId,     'num_followers', increment=-1)

        # Remove stamps from Inbox
        stampIds = self._collectionDB.getUserStampIds(userId)
        self._stampDB.removeInboxStampReferencesForUser(authUserId, stampIds)

    def approveFriendship(self, data, auth):
        raise NotImplementedError

    def checkFriendship(self, authUserId, userRequest):
        userA = self._users.getUserFromIdOrScreenName({
                    'user_id': userRequest.user_id_a,
                    'screen_name': userRequest.screen_name_a
                })
        userB = self._users.getUserFromIdOrScreenName({
                    'user_id': userRequest.user_id_b,
                    'screen_name': userRequest.screen_name_b
                })

        # If either account is private, make sure authUserId is friend
        if userA.privacy == True and authUserId != userA.user_id:
            check                   = Friendship()
            friendship.user_id      = authUserId
            friendship.friend_id    = userA.user_id

            if not self._friendshipDB.checkFriendship(check):
                raise StampedFriendshipCheckPermissionsError("Insufficient privileges to check friendship")

        if userB.privacy == True and authUserId != userB.user_id:
            check                   = Friendship()
            friendship.user_id      = authUserId
            friendship.friend_id    = userB.user_id

            if not self._friendshipDB.checkFriendship(check):
                raise StampedFriendshipCheckPermissionsError("Insufficient privileges to check friendship")

        friendship              = Friendship()
        friendship.user_id      = userA.user_id
        friendship.friend_id    = userB.user_id

        return self._friendshipDB.checkFriendship(friendship)

    def getFriends(self, userRequest):
        # TODO (travis): optimization - no need to query DB for user here if userRequest already contains user_id!
        user = self._users.getUserFromIdOrScreenName(userRequest)

        # Note: This function returns data even if user is private

        friends = self._friendshipDB.getFriends(user.user_id)

        # Return data in reverse-chronological order
        friends.reverse()

        return friends
    
    def getEnrichedFriends(self, user_id, limit=100):
        user_ids = self._friendshipDB.getFriends(user_id, limit=limit)
        
        # Return data in reverse-chronological order
        user_ids.reverse()
        
        return self._userDB.lookupUsers(user_ids, None, limit=limit)
    
    def getFollowers(self, userRequest):
        # TODO (travis): optimization - no need to query DB for user here if userRequest already contains user_id!
        user = self._users.getUserFromIdOrScreenName(userRequest)
        
        # Note: This function returns data even if user is private
        
        followers = self._friendshipDB.getFollowers(user.user_id)
        
        # Return data in reverse-chronological order
        followers.reverse()
        
        return followers
    
    def getEnrichedFollowers(self, user_id, limit=100):
        user_ids = self._friendshipDB.getFollowers(user_id, limit=limit)
        
        # Return data in reverse-chronological order
        user_ids.reverse()
        
        return self._userDB.lookupUsers(user_ids, None, limit=limit)
    
    def addBlock(self, authUserId, userRequest):
        user = self._users.getUserFromIdOrScreenName(userRequest)

        friendship                      = Friendship()
        friendship.user_id              = authUserId
        friendship.friend_id            = user.user_id

        reverseFriendship               = Friendship()
        reverseFriendship.user_id       = user.user_id
        reverseFriendship.friend_id     = authUserId

        # Check if block already exists
        if self._friendshipDB.checkBlock(friendship) == True:
            logs.info("Block exists")
            return user

        # Add block
        self._friendshipDB.addBlock(friendship)

        # Destroy friendships
        self._friendshipDB.removeFriendship(friendship)
        self._friendshipDB.removeFriendship(reverseFriendship)

        return user

    def checkBlock(self, authUserId, userRequest):
        user                    = self._users.getUserFromIdOrScreenName(userRequest)
        friendship              = Friendship()
        friendship.user_id      = authUserId
        friendship.friend_id    = user.user_id

        if self._friendshipDB.checkBlock(friendship):
            return True

        return False

    def getBlocks(self, authUserId):
        return self._friendshipDB.getBlocks(authUserId)

    def removeBlock(self, authUserId, userRequest):
        user                    = self._users.getUserFromIdOrScreenName(userRequest)
        friendship              = Friendship()
        friendship.user_id      = authUserId
        friendship.friend_id    = user.user_id

        # Check if block already exists
        if self._friendshipDB.checkBlock(friendship) == False:
            logs.info("Block does not exist")
            return user

        self._friendshipDB.removeBlock(friendship)

        ### TODO: Reenable activity items that were hidden before

        return user

    def inviteFriends(self, authUserId, emails):
        for email in emails:
            # Store email address linked to auth user id
            self.call_task(self.inviteFriendsAsync, {'authUserId': authUserId, 'email': email})
        return True

    def inviteFriendsAsync(self, authUserId, email):
        # Validate email address
        email = str(email).lower().strip()
        email = SchemaValidation.validateEmail(email)

        if self._inviteDB.checkInviteExists(email, authUserId):
            logs.info("Invite already exists")
            return

        self._inviteDB.inviteUser(email, authUserId)
