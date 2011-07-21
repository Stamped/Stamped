#!/usr/bin/python

__author__ = 'Stamped (dev@stamped.com)'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__ = 'TODO'

import copy

from threading import Lock
from datetime import datetime

from MongoDB import Mongo
# from api.AFriendshipDB import AFriendshipDB
# from api.Friendship import Friendship

class MongoStampComments(Mongo):
        
    COLLECTION = 'stampcomments'
        
    SCHEMA = {
        '_id': basestring,
        'comment_id': basestring
    }
    
    def __init__(self, setup=False):
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def addStampComment(self, stampId, commentId):
        
        if not isinstance(stampId, basestring) or not isinstance(commentId, basestring):
            raise KeyError("ID not valid")
        self._createRelationship(keyId=stampId, refId=commentId)
        return True
        
    def addStampComments(self, stampIds, commentId):
        for stampId in stampIds:
            self.addStampComment(stampId, commentId)
        return True
            
    def removeStampComment(self, stampId, commentId):
        return self._removeRelationship(keyId=stampId, refId=commentId)
            
    def getStampCommentIds(self, stampId, limit=None):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(stampId, limit)


    ### PRIVATE
    
