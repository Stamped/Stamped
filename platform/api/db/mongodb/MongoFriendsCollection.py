#!/usr/bin/env python
from __future__ import absolute_import

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from api.db.mongodb.AMongoCollection import AMongoCollection

class MongoFriendsCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='friends')
    
    ### PUBLIC
    
    def addFriend(self, userId, friendId):
        self._createRelationship(keyId=userId, refId=friendId)
        return True
    
    def checkFriend(self, userId, friendId):
        return self._checkRelationship(keyId=userId, refId=friendId)
    
    def removeFriend(self, userId, friendId):
        return self._removeRelationship(keyId=userId, refId=friendId)
    
    def getFriends(self, userId, limit=None):
        return self._getRelationships(userId, limit)
    
    def removeAllFriends(self, userId):
        return self._removeAllRelationships(userId)

