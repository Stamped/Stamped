#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

import logs
from utils import lazyProperty

from db.mongodb.MongoFriendsCollection import MongoFriendsCollection
from db.mongodb.MongoFollowersCollection import MongoFollowersCollection
from db.mongodb.MongoBlockCollection import MongoBlockCollection

class FriendshipDB(object):

    @lazyProperty
    def __friends_collection(self):
        return MongoFriendsCollection()

    @lazyProperty
    def __followers_collection(self):
        return MongoFollowersCollection()
    

    def addFriendship(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Add Friendship: %s -> %s" % (userId, friendId))
        self.__friends_collection.addFriend(userId=userId, friendId=friendId)
        self.__followers_collection.addFollower(userId=friendId, followerId=userId)
        return True
    
    def checkFriendship(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Check Friendship: %s -> %s" % (userId, friendId))
        status = self.__friends_collection.checkFriend(userId=userId, friendId=friendId)
        return status
    
    def removeFriendship(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Remove Friendship: %s -> %s" % (userId, friendId))
        self.__friends_collection.removeFriend(userId=userId, friendId=friendId)
        self.__followers_collection.removeFollower(userId=friendId, followerId=userId)
        return True
    
    def getFriends(self, userId, limit=None):
        # TODO: add cursor support
        return self.__friends_collection.getFriends(userId, limit)
    
    def getFollowers(self, userId, limit=None):
        # TODO: add cursor support
        return self.__followers_collection.getFollowers(userId, limit)
    
    def countFriends(self, userId):
        return len(self.__friends_collection.getFriends(userId))
    
    def countFollowers(self, userId):
        return len(self.__followers_collection.getFollowers(userId))
    
    ### DEPRECATED

    @lazyProperty
    def __block_collection(self):
        return MongoBlockCollection()
    
    def addBlock(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Add Block: %s -> %s" % (userId, friendId))
        self.__block_collection.addBlock(userId=userId, friendId=friendId)
    
    # One Way (Is User A blocking User B?)
    def checkBlock(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Check Block: %s -> %s" % (userId, friendId))
        status = self.__block_collection.checkBlock(userId=userId, friendId=friendId)
        return status
    
    # Two Way (Is User A blocking User B or blocked by User B?)
    def blockExists(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Check Block: %s -> %s" % (userId, friendId))
        statusA = self.__block_collection.checkBlock(userId=userId, friendId=friendId)
        
        logs.debug("Check Block: %s -> %s" % (friendId, userId))
        statusB = self.__block_collection.checkBlock(userId=friendId, friendId=userId)
        
        if statusA or statusB:
            return True
        return False
    
    def removeBlock(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Remove Block: %s -> %s" % (userId, friendId))
        return self.__block_collection.removeBlock(userId=userId, friendId=friendId)
    
    def getBlocks(self, userId):
        return self.__block_collection.getBlocks(userId)
