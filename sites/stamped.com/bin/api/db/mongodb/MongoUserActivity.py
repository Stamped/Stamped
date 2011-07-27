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

class MongoUserActivity(Mongo):
        
    COLLECTION = 'useractivity'
        
    SCHEMA = {
        '_id': basestring,
        'activity_id': basestring
    }
    
    def __init__(self, setup=False):
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def addUserActivity(self, userId, activityId):
        
        if not isinstance(userId, basestring) or not isinstance(activityId, basestring):
            raise KeyError("ID not valid")
        
        self._createRelationship(keyId=userId, refId=activityId)
        return True
            
    def removeUserActivity(self, userId, activityId):
        return self._removeRelationship(keyId=userId, refId=activityId)
            
    def getUserActivityIds(self, userId):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(userId)


    ### PRIVATE
    
