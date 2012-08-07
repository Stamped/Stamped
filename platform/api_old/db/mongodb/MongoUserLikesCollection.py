#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from db.mongodb.AMongoCollection import AMongoCollection

from libs.Memcache import globalMemcache

class MongoUserLikesCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='userlikes')

        self._cache = globalMemcache()


    """
    User Id -> Stamp Ids 
    """


    ### CACHING

    def _getCachedRelationship(self, userId):
        key = str("obj::userlikes::%s" % userId)
        return self._cache[key]

    def _setCachedRelationship(self, userId, stampIds):
        key = str("obj::userlikes::%s" % userId)
        cacheLength = 60 * 60 * 3 # 3 hours
        try:
            self._cache.set(key, stampIds, time=cacheLength)
        except Exception as e:
            logs.warning("Unable to set cache for %s: %s" % (userId, e))

    def _delCachedRelationship(self, userId):
        key = str("obj::userlikes::%s" % userId)
        try:
            del(self._cache[key])
        except KeyError:
            pass


    ### INTEGRITY

    def checkIntegrity(self, key, repair=True, api=None):

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
        self._delCachedRelationship(userId)
        return True
            
    def removeUserLike(self, userId, stampId):
        result = self._removeRelationship(keyId=userId, refId=stampId)
        self._delCachedRelationship(userId)
        return result
            
    def getUserLikes(self, userId):
        ### TODO: Add limit? Add timestamp to slice?
        try:
            return self._getCachedRelationship(userId)
        except KeyError:
            pass

        stampIds = self._getRelationships(userId)

        self._setCachedRelationship(userId, stampIds)

        return stampIds
        

