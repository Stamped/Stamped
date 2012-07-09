#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from api.db.mongodb.AMongoCollection import AMongoCollection

class MongoUserLikesCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='userlikes')

    """
    User Id -> Stamp Ids 
    """

    ### INTEGRITY

    def checkIntegrity(self, key, repair=True):

        def regenerate(key):
            stampIds = set()
            stamps = self._collection._database['stamplikes'].find({'ref_ids': key}, fields=['_id'])
            for stamp in stamps:
                stampIds.add(str(stamp['_id']))

            return { '_id' : key, 'ref_ids' : list(stampIds) }

        def keyCheck(key):
            assert self._collection._database['users'].find({'_id': self._getObjectIdFromString(key)}).count() == 1

        return self._checkRelationshipIntegrity(key, keyCheck, regenerate, repair=repair)
    
    ### PUBLIC
    
    def addUserLike(self, userId, stampId):
        self._createRelationship(keyId=userId, refId=stampId)
        return True
            
    def removeUserLike(self, userId, stampId):
        return self._removeRelationship(keyId=userId, refId=stampId)
            
    def getUserLikes(self, userId, limit=None):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(userId, limit)
        

