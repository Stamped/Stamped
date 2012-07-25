#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals
import logs
import pymongo

from api.db.mongodb.AMongoCollection import AMongoCollection

class MongoInboxStampsCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='inboxstamps')
        self._collection._database['stamps'].ensure_index([('user.user_id', pymongo.ASCENDING)])
        

    """
    User Id -> Stamp Ids 
    """

    ### INTEGRITY

    def checkIntegrity(self, key, repair=True, api=None):

        def regenerate(key):
            userIds = set([ key ])

            friends = self._collection._database['friends'].find_one({'_id' : key})
            if friends is not None:
                userIds = userIds.union(set(friends['ref_ids']))

            stampIds = set()
            for userId in userIds:
                stamps = self._collection._database['stamps'].find({'user.user_id': userId}, fields=['_id'])
                for stamp in stamps:
                    stampIds.add(str(stamp['_id']))

            return { '_id' : key, 'ref_ids' : list(stampIds) }

        def keyCheck(key):
            assert self._collection._database['users'].find({'_id': self._getObjectIdFromString(key)}).count() == 1

        return self._checkRelationshipIntegrity(key, keyCheck, regenerate, repair=repair)
    
    ### PUBLIC
    
    def addInboxStamp(self, userId, stampId):
        if not isinstance(userId, basestring) or not isinstance(stampId, basestring):
            raise KeyError("ID not valid")
        
        self._createRelationship(keyId=userId, refId=stampId)
        return True
        
    def addInboxStamps(self, userIds, stampId):
        for userId in userIds:
            self.addInboxStamp(userId, stampId)
        return True
            
    def removeInboxStamp(self, userId, stampId):
        return self._removeRelationship(keyId=userId, refId=stampId)

    def removeInboxStamps(self, userIds, stampId):
        for userId in userIds:
            self.removeInboxStamp(userId, stampId)
        return True
            
    def getInboxStampIds(self, userId, since=None, limit=None):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(userId, limit)
        
    def checkInboxStamp(self, userID, stampID):
        return self._checkRelationship(keyId=userId, refId=stampId)

    def addInboxStampsForUser(self, userId, stampIds):
        ### TODO: Make this more efficient
        for stampId in stampIds:
            self.addInboxStamp(userId, stampId)
        return True

    def removeInboxStampsForUser(self, userId, stampIds):
        ### TODO: Make this more efficient
        for stampId in stampIds:
            self.removeInboxStamp(userId, stampId)
        return True

    def removeAllInboxStamps(self, userId):
        return self._removeAllRelationships(userId)

