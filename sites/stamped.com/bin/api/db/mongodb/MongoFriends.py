#!/usr/bin/python

__author__ = 'Stamped (dev@stamped.com)'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__ = 'TODO'

import copy

from threading import Lock
from datetime import datetime

from MongoDB import Mongo

class MongoFriends(Mongo):
        
    COLLECTION = 'friends'
        
    SCHEMA = {
        '_id': basestring,
        'friend_id': basestring,
        'timestamp': basestring
    }
    
    def __init__(self, setup=False):
#         AFriendshipDB.__init__(self, self.DESC)
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def addFriend(self, userId, friendId):
        self._createRelationship(keyId=userId, refId=friendId)
        return True
    
    def checkFriend(self, userId, friendId):
        return self._checkRelationship(keyId=userId, refId=friendId)
            
    def removeFriend(self, userId, friendId):
        return self._removeRelationship(keyId=userId, refId=friendId)
            
    def getFriends(self, userId):
        return self._getRelationships(userId)


    ### PRIVATE
    
