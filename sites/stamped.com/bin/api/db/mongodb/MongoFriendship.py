#!/usr/bin/python

__author__ = 'Stamped (dev@stamped.com)'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__ = 'TODO'

import Globals
import copy

from threading import Lock
from datetime import datetime

from api.AFriendshipDB import AFriendshipDB
from api.Friendship import Friendship
from MongoDB import Mongo
from MongoUser import MongoUser
from MongoFriends import MongoFriends
from MongoFollowers import MongoFollowers
from MongoBlock import MongoBlock

class MongoFriendship(AFriendshipDB):
        
    SCHEMA = {
        '_id': basestring,
        'friend_id': basestring
    }
    
    DESC = 'Mongo Friendship Wrapper'
    
    def __init__(self, setup=False):
        AFriendshipDB.__init__(self, self.DESC)
        
        
    ### PUBLIC
    
    def addFriendship(self, friendship):
    
        friendship = self._objToMongo(friendship)
        userId = friendship['_id']
        friendId = friendship['friend_id']
        
        # Check if friendship already exists (???)
        
        # If block exists, don't surface friend request; otherwise add to queue
        if MongoBlock().checkBlock(userId, friendId):
            ### TODO: Log request somewhere
            return False
        
        if MongoUser().checkPrivacy(friendId):
            # Request approval before creating friendship
            
            ### TODO: Add to queue                    
            return False
            
        else:
            # Create friendship
            MongoFriends().addFriend(userId=userId, friendId=friendId)
            MongoFollowers().addFollower(userId=friendId, followerId=userId)
            return True
            
    def checkFriendship(self, friendship):
        friendship = self._objToMongo(friendship)
        return MongoFriends().checkFriend(userId=friendship['_id'], friendId=friendship['friend_id'])
            
    def removeFriendship(self, friendship):
        friendship = self._objToMongo(friendship)
        return self._destroyFriendship(userId=friendship['_id'], friendId=friendship['friend_id'])
            
    def getFriends(self, userId):
        return MongoFriends().getFriends(userId)
            
    def getFollowers(self, userId):
        return MongoFollowers().getFollowers(userId)

    def approveFriendship(self, friendship):
        ### TODO
        print 'TODO'
    
    def addBlock(self, friendship):
        friendship = self._objToMongo(friendship)
        try:
            MongoBlock().addBlock(userId=friendship['_id'], friendId=friendship['friend_id'])
            self._destroyFriendship(userId=friendship['_id'], friendId=friendship['friend_id'])
            self._destroyFriendship(userId=friendship['friend_id'], friendId=friendship['_id'])
            return True
        except:
            return False
    
    def checkBlock(self, friendship):
        friendship = self._objToMongo(friendship)
        return MongoBlock().checkBlock(userId=friendship['_id'], friendId=friendship['friend_id'])
            
    def removeBlock(self, friendship):
        friendship = self._objToMongo(friendship)
        return MongoBlock().removeBlock(userId=friendship['_id'], friendId=friendship['friend_id'])
            
    def getBlocks(self, userId):
        return MongoBlock().getBlocks(userId)
    
            
    ### PRIVATE
    
    def _destroyFriendship(self, userId, friendId):
        try:
            MongoFriends().removeFriend(userId=userId, friendId=friendId)
            MongoFollowers().removeFollower(userId=friendId, followerId=userId)
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

