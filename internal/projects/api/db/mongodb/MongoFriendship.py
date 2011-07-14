#!/usr/bin/python

__author__ = 'Stamped (dev@stamped.com)'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__ = 'TODO'

import copy

from threading import Lock
from datetime import datetime

from MongoDB import Mongo
from AFriendshipDB import AFriendshipDB
from Friendship import Friendship
from MongoUser import MongoUser
from MongoFriends import MongoFriends
from MongoFollowers import MongoFollowers

class MongoFriendship(AFriendshipDB):
        
    SCHEMA = {
        '_id': basestring,
        'friend_id': basestring
    }
    
    DESC = 'Mongo Friends Wrapper'
    
    def __init__(self, setup=False):
        AFriendshipDB.__init__(self, self.DESC)
        
        
    ### PUBLIC
    
    def addFriendship(self, friendship):
    
        friendship = self._objToMongo(friendship)
        userId = friendship['_id']
        friendId = friendship['friend_id']
        
        # Check if friendship already exists (???)
        
        # Check if block exists
        
        # Check if following_id is private
        if MongoUser().checkPrivacy(userId):
            # Request approval before creating friendship
            print 'TODO: Locked account friendship request'
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
        userId = friendship['_id']
        friendId = friendship['friend_id']
        
        try:
            MongoFriends().removeFriend(userId=userId, friendId=friendId)
            MongoFollowers().removeFollower(userId=friendId, followerId=userId)
            return True
        except:
            return False
            
    def getFriends(self, userId):
        return MongoFriends().getFriends(userId)
            
    def getFollowers(self, userId):
        return MongoFollowers().getFollowers(userId)

    def approveFriendship(self, friendship):
        ### TODO
        print 'TODO'
            
            
    ### PRIVATE

    def _objToMongo(self, obj):
        if obj.isValid == False:
            print obj
            raise KeyError('Object not valid')
        data = {}
        data['_id'] = obj.user_id
        data['friend_id'] = obj.friend_id
        return data

