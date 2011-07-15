#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from threading import Lock
from datetime import datetime

from MongoDB import Mongo

class MongoBlock(Mongo):
        
    COLLECTION = 'blocks'
        
    SCHEMA = {
        'user_id': basestring,
        'blocked_id': basestring,
        'timestamp': basestring
    }
    
    def __init__(self, setup=False):
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def addBlock(self, userId, friendId):
        self._createRelationship(keyId=userId, refId=friendId)
        return True
    
    def checkBlock(self, userId, friendId):
        return self._checkRelationship(keyId=userId, refId=friendId)
            
    def removeBlock(self, userId, friendId):
        return self._removeRelationship(keyId=userId, refId=friendId)
            
    def getBlocks(self, userId):
        return self._getRelationships(userId)
        
        
    ### PRIVATE
        
#     def _objToMongo(self, obj):
#         if obj.isValid == False:
#             print obj
#             raise KeyError('Object not valid')
#         data = {}
#         data['user_id'] = obj.user_id
#         data['blocked_id'] = obj.blocked_user_id
#         return data
