#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from api.db.mongodb.AMongoCollection import AMongoCollection

class MongoUserStampsCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='userstamps')
    
    ### PUBLIC
    
    def addUserStamp(self, userId, stampId):
        if not isinstance(userId, basestring) or not isinstance(stampId, basestring):
            raise KeyError("ID not valid")
        
        self._createRelationship(keyId=userId, refId=stampId)
        return True
    
    def removeUserStamp(self, userId, stampId):
        return self._removeRelationship(keyId=userId, refId=stampId)
    
    def getUserStampIds(self, userId, limit=None):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(userId, limit)
    
    def removeAllUserStamps(self, userId):
        return self._removeAllRelationships(userId)

