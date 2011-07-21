#!/usr/bin/python

__author__ = 'Stamped (dev@stamped.com)'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__ = 'TODO'

import Globals
import copy

from threading import Lock
from datetime import datetime

from MongoDB import Mongo
# from api.AFriendshipDB import AFriendshipDB
# from api.Friendship import Friendship

class MongoInboxStamps(Mongo):
        
    COLLECTION = 'inboxstamps'
        
    SCHEMA = {
        '_id': basestring,
        'stamp_id': basestring
    }
    
    def __init__(self, setup=False):
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def addInboxStamp(self, userId, stampId):
        
        if not isinstance(userId, basestring) or not isinstance(stampId, basestring):
            raise KeyError("ID not valid")
        self._createRelationship(keyId=userId, refId=stampId)
        return True
        
    def addInboxStamps(self, userIds, stampId):
        for userId in userIds:
            self.addInboxStamp(userId, stampId)
        return True
            
    def removeInboxStamp(self, userId, stampId):
        return self._removeRelationship(keyId=userId, refId=stampId)
            
    def getInboxStampIds(self, userId, limit=None):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(userId, limit)
        
    def checkInboxStamp(self, userID, stampID):
        return self._checkRelationship(keyId=userId, refId=stampId)


    ### PRIVATE
    
