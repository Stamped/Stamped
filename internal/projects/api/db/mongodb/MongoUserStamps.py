#!/usr/bin/python

__author__ = 'Stamped (dev@stamped.com)'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__ = 'TODO'

import copy

from threading import Lock
from datetime import datetime

from MongoDB import Mongo
# from AFriendshipDB import AFriendshipDB
# from Friendship import Friendship
# from MongoUser import MongoUser

class MongoUserStamps(Mongo):
        
    COLLECTION = 'userstamps'
        
    SCHEMA = {
        '_id': basestring,
        'stamp_id': basestring
    }
    
    def __init__(self, setup=False):
#         AFriendshipDB.__init__(self, self.DESC)
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def addUserStamp(self, userId, stampId):
        
        if not isinstance(userId, basestring) or not isinstance(stampId, basestring):
            raise KeyError("ID not valid")
        
        self._createRelationship(keyId=userId, refId=stampId)
        return True
            
    def removeUserStamp(self, userId, stampId):
        return self._removeRelationship(keyId=userId, refId=stampId)
            
    def getUserStamps(self, userId):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(userId)


    ### PRIVATE
    