#!/usr/bin/python

__author__ = 'Stamped (dev@stamped.com)'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__ = 'TODO'

import copy

from threading import Lock
from datetime import datetime

from MongoDB import Mongo

class MongoFollowers(Mongo):
        
    COLLECTION = 'followers'
        
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
    
    def addFollower(self, userId, followerId):
        self._createRelationship(keyId=userId, refId=followerId)
        return True
    
    def checkFollowing(self, userId, followerId):
        return self._checkRelationship(keyId=userId, refId=followerId)
            
    def removeFollower(self, userId, followerId):
        return self._removeRelationship(keyId=userId, refId=followerId)
            
    def getFollowers(self, userId):
        return self._getRelationships(userId)


    ### PRIVATE
