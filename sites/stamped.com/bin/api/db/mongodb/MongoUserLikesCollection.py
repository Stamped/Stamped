#!/usr/bin/python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__   = 'TODO'

import Globals

from AMongoCollection import AMongoCollection

class MongoUserLikesCollection(AMongoCollection):
    
    SCHEMA = {
        '_id': basestring,
        'stamp_id': basestring
    }
    
    def __init__(self, setup=False):
        AMongoCollection.__init__(self, collection='userlikes')
    
    ### PUBLIC
    
    def addUserLike(self, userId, stampId):
        self._createRelationship(keyId=userId, refId=stampId)
        return True
            
    def removeUserLike(self, userId, stampId):
        return self._removeRelationship(keyId=userId, refId=stampId)
            
    def getUserLikes(self, userId, limit=None):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(userId, limit)
        

