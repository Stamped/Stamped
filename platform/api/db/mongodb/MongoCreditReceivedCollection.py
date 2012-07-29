#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals, pymongo

from api.db.mongodb.AMongoCollection import AMongoCollection

class MongoCreditReceivedCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='creditreceived')

        self._collection.ensure_index([('credits.user.user_id', pymongo.ASCENDING)])
        self._collection.ensure_index([('ref_ids', pymongo.ASCENDING)])

    """
    Credited User Id -> Stamp Ids 
    """

    ### INTEGRITY

    def checkIntegrity(self, key, repair=False, api=None):

        def regenerate(key):
            stampIds = set()
            stamps = self._collection._database['stamps'].find({'credits.user.user_id': key}, fields=['_id'])
            for stamp in stamps:
                stampIds.add(str(stamp['_id']))

            return { '_id' : key, 'ref_ids' : list(stampIds) }

        def keyCheck(key):
            assert self._collection._database['users'].find({'_id': self._getObjectIdFromString(key)}).count() == 1

        return self._checkRelationshipIntegrity(key, keyCheck, regenerate, repair=repair)
    
    ### PUBLIC
    
    def addCredit(self, userId, stampId):
        self._createRelationship(keyId=userId, refId=stampId)
        return self.numCredit(userId)
    
    def removeCredit(self, userId, stampId):
        return self._removeRelationship(keyId=userId, refId=stampId)
            
    def getCredit(self, userId):
        return self._getRelationships(userId)
        
    def numCredit(self, userId):
        return len(self.getCredit(userId))

