#!/usr/bin/python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from AMongoCollection import AMongoCollection

class MongoStampLikesCollection(AMongoCollection):
    
    SCHEMA = {
        '_id': basestring,
        'user_id': basestring
    }
    
    def __init__(self, setup=False):
        AMongoCollection.__init__(self, collection='stamplikes')
    
    ### PUBLIC
    
    def addStampLike(self, stampId, userId):
        self._createRelationship(keyId=stampId, refId=userId)
        return True
        
    def addStampLikes(self, stampIds, userId):
        for stampId in stampIds:
            self.addStampLike(stampId, userId)
        return True
            
    def removeStampLike(self, stampId, userId):
        return self._removeRelationship(keyId=stampId, refId=userId)
            
    def getStampLikes(self, stampId, limit=None):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(stampId, limit)
        
