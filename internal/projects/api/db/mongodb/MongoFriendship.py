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

class MongoFriendship(AFriendshipDB, Mongo):
        
    COLLECTION = 'friendships'
        
    SCHEMA = {
        '_id': basestring,
        'friend_id': basestring,
        'timestamp': basestring
    }
    
    def __init__(self, setup=False):
        AFriendshipDB.__init__(self, self.DESC)
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def addFriendship(self, friendship):
        
        friendship = self._objToMongo(friendship)
        
        # Check if friendship already exists (???)
        
        # Check if block exists
        
        # Check if following_id is private
        if MongoUser().checkPrivacy(friendship['friend_id']):
            # Request approval before creating friendship
            print 'TODO: Locked account friendship request'
            return False
            
        else:
            # Create friendship
            self._createRelationship(keyId=friendship['_id'], refId=friendship['friend_id'])
#             self._createFollower(userId=friendship['friend_id'], followerId=friendship['_id'])
            return True
    
    def checkFriendship(self, friendship):
        return self._checkRelationship(keyId=friendship['user_id'], 
                                        refId=friendship['friend_id'])
            
    def removeFriendship(self, friendship):
        return self._removeRelationship(keyId=friendship['user_id'], 
                                        refId=friendship['friend_id'])
            
    def getFriendships(self, userId):
        return self._getRelationships(userId)

    def approveFriendship(self, friendship):
        ### TODO
        print 'TODO'


    ### PRIVATE
    
    def _objToMongo(self, obj):
        if obj.isValid == False:
            print obj
            raise KeyError('Object not valid')
        data = copy.copy(obj.getDataAsDict())
        data['_id'] = data['user_id']
        del(data['user_id'])
        return self._mapDataToSchema(data, self.SCHEMA)
