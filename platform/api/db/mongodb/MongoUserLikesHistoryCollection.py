#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from AMongoCollection import AMongoCollection

class MongoUserLikesHistoryCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='userlikeshistory')
    
    ### PUBLIC
    
    def addUserLike(self, userId, stampId):
        self._createRelationship(keyId=userId, refId=stampId)
        return True
            
    def getUserLikes(self, userId, limit=None):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(userId, limit)
        

