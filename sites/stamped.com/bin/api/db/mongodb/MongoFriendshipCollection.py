#!/usr/bin/python

__author__ = 'Stamped (dev@stamped.com)'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__ = 'TODO'

import Globals, logs

from utils import lazyProperty

from AMongoCollection import AMongoCollection
from MongoUserCollection import MongoUserCollection
from MongoFriendsCollection import MongoFriendsCollection
from MongoFollowersCollection import MongoFollowersCollection
from MongoBlockCollection import MongoBlockCollection

from api.AFriendshipDB import AFriendshipDB
from api.Friendship import Friendship

class MongoFriendshipCollection(AFriendshipDB):
    
    ### PUBLIC
    
    @lazyProperty
    def block_collection(self):
        return MongoBlockCollection()
    
    @lazyProperty
    def user_collection(self):
        return MongoUserCollection()
    
    @lazyProperty
    def friends_collection(self):
        return MongoFriendsCollection()
    
    @lazyProperty
    def followers_collection(self):
        return MongoFollowersCollection()
    
    def addFriendship(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Add Friendship: %s -> %s" % (userId, friendId))
        self.friends_collection.addFriend(userId=userId, friendId=friendId)
        self.followers_collection.addFollower(userId=friendId, followerId=userId)
        return True
    
    def checkFriendship(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id

        logs.debug("Check Friendship: %s -> %s" % (userId, friendId))
        status = self.friends_collection.checkFriend(userId=userId, \
            friendId=friendId)
        return status
            
    def removeFriendship(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id

        logs.debug("Remove Friendship: %s -> %s" % (userId, friendId))
        self.friends_collection.removeFriend(userId=userId, friendId=friendId)
        self.followers_collection.removeFollower(userId=friendId, followerId=userId)
        return True
            
    def getFriends(self, userId):
        return self.friends_collection.getFriends(userId)
            
    def getFollowers(self, userId):
        return self.followers_collection.getFollowers(userId)

    def approveFriendship(self, friendship):
        ### TODO
        raise NotImplementedError
    
    def addBlock(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id

        logs.debug("Add Block: %s -> %s" % (userId, friendId))
        self.block_collection.addBlock(userId=userId, friendId=friendId)
    
    def checkBlock(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id

        logs.debug("Check Block: %s -> %s" % (userId, friendId))
        status = self.block_collection.checkBlock(userId=userId, \
            friendId=friendId)
        return status
            
    def removeBlock(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id

        logs.debug("Remove Block: %s -> %s" % (userId, friendId))
        return self.block_collection.removeBlock(userId=userId, \
            friendId=friendId)
            
    def getBlocks(self, userId):
        return self.block_collection.getBlocks(userId)

