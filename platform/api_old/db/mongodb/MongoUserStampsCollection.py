#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from db.mongodb.AMongoCollection import AMongoCollection

class MongoUserStampsCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='userstamps')

    ### INTEGRITY

    def checkIntegrity(self, key, repair=True, api=None):

        def regenerate(key):
            stampIds = set()
            stamps = self._collection._database['stamps'].find({'user.user_id': key}, fields=['_id'])
            for stamp in stamps:
                stampIds.add(str(stamp['_id']))

            return { '_id' : key, 'ref_ids' : list(stampIds) }

        def keyCheck(key):
            assert self._collection._database['users'].find({'_id': self._getObjectIdFromString(key)}).count() == 1

        return self._checkRelationshipIntegrity(key, keyCheck, regenerate, repair=repair)
    
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

