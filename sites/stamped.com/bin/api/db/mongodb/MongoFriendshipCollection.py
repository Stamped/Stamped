#!/usr/bin/python

__author__ = 'Stamped (dev@stamped.com)'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__ = 'TODO'

import Globals

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
        friendship = self._objToMongo(friendship)
        userId = friendship['_id']
        friendId = friendship['friend_id']
        
        # TODO: Check if friendship already exists (???)
        
        # If block exists, don't surface friend request; otherwise add to queue
        if self.block_collection.checkBlock(userId, friendId):
            ### TODO: Log request somewhere
            return False
        
        if self.user_collection.checkPrivacy(userId):
            # Request approval before creating friendship
            
            ### TODO: Add to queue                    
            return False
        else:
            # Create friendship
            self.friends_collection.addFriend(userId=userId, friendId=friendId)
            self.followers_collection.addFollower(userId=friendId, followerId=userId)
            return True
    
    def checkFriendship(self, friendship):
        friendship = self._objToMongo(friendship)
        return self.friends_collection.checkFriend(userId=friendship['_id'], friendId=friendship['friend_id'])
            
    def removeFriendship(self, friendship):
        friendship = self._objToMongo(friendship)
        return self._destroyFriendship(userId=friendship['_id'], friendId=friendship['friend_id'])
            
    def getFriends(self, userId):
        return self.friends_collection.getFriends(userId)
            
    def getFollowers(self, userId):
        return self.followers_collection.getFollowers(userId)

    def approveFriendship(self, friendship):
        ### TODO
        print 'TODO'
    
    def addBlock(self, friendship):
        friendship = self._objToMongo(friendship)
        try:
            self.block_collection.addBlock(userId=friendship['_id'], friendId=friendship['friend_id'])
            self._destroyFriendship(userId=friendship['_id'], friendId=friendship['friend_id'])
            self._destroyFriendship(userId=friendship['friend_id'], friendId=friendship['_id'])
            return True
        except:
            return False
    
    def checkBlock(self, friendship):
        friendship = self._objToMongo(friendship)
        return self.block_collection.checkBlock(userId=friendship['_id'], friendId=friendship['friend_id'])
            
    def removeBlock(self, friendship):
        friendship = self._objToMongo(friendship)
        return self.block_collection.removeBlock(userId=friendship['_id'], friendId=friendship['friend_id'])
            
    def getBlocks(self, userId):
        return self.block_collection.getBlocks(userId)
    
    ### PRIVATE
    
    def _destroyFriendship(self, userId, friendId):
        try:
            self.friends_collection.removeFriend(userId=userId, friendId=friendId)
            self.followers_collection.removeFollower(userId=friendId, followerId=userId)
            return True
        except:
            return False
    
    def _objToMongo(self, obj):
        if obj.isValid == False:
            print obj
            raise KeyError('Object not valid')
        
        data = {}
        data['_id'] = obj.user_id
        data['friend_id'] = obj.friend_id
        return data

