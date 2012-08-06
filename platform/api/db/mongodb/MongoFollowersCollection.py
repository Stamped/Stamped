#!/usr/bin/env python
from __future__ import absolute_import

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from api.db.mongodb.AMongoCollection import AMongoCollection

class MongoFollowersCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='followers')
    
    ### PUBLIC
    
    def addFollower(self, userId, followerId):
        self._createRelationship(keyId=userId, refId=followerId)
        return True
    
    def checkFollowing(self, userId, followerId):
        return self._checkRelationship(keyId=userId, refId=followerId)
            
    def removeFollower(self, userId, followerId):
        return self._removeRelationship(keyId=userId, refId=followerId)
            
    def getFollowers(self, userId, limit=None):
        return self._getRelationships(userId, limit)

    def removeAllFollowers(self, userId):
        return self._removeAllRelationships(userId)

