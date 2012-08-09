#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from utils import lazyProperty

from db.mongodb.MongoFriendsCollection import MongoFriendsCollection
from db.mongodb.MongoFollowersCollection import MongoFollowersCollection

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
    