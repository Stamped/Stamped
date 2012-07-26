#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from api.db.mongodb.AMongoCollection import AMongoCollection

from libs.Memcache import globalMemcache

class MongoUserTodosEntitiesCollection(AMongoCollection):

    def __init__(self):
        AMongoCollection.__init__(self, collection='userfaventities')

        self._cache = globalMemcache()
            

    """
    User Id -> Entity Ids 
    """


    ### CACHING

    def _getCachedRelationship(self, userId):
        key = str("obj::userfaventities::%s" % userId)
        return self._cache[key]

    def _setCachedRelationship(self, userId, entityIds):
        key = str("obj::userfaventities::%s" % userId)
        cacheLength = 60 * 60 * 3 # 3 hours
        try:
            self._cache.set(key, entityIds, time=cacheLength)
        except Exception as e:
            logs.warning("Unable to set cache for %s: %s" % (userId, e))

    def _delCachedRelationship(self, userId):
        key = str("obj::userfaventities::%s" % userId)
        try:
            del(self._cache[key])
        except KeyError:
            pass


    ### INTEGRITY

    def checkIntegrity(self, key, repair=True, api=None):

        def regenerate(key):
            entityIds = set()
            todos = self._collection._database['favorites'].find({'user_id': key}, fields=['entity.entity_id'])
            for todo in todos:
                entityIds.add(str(todo['entity']['entity_id']))

            return { '_id' : key, 'ref_ids' : list(entityIds) }

        def keyCheck(key):
            assert self._collection._database['users'].find({'_id': self._getObjectIdFromString(key)}).count() == 1

        return self._checkRelationshipIntegrity(key, keyCheck, regenerate, repair=repair)


    ### PUBLIC

    def addUserTodosEntity(self, userId, entityId):
        self._createRelationship(keyId=userId, refId=entityId)
        self._delCachedRelationship(userId)
        return True

    def removeUserTodosEntity(self, userId, entityId):
        result = self._removeRelationship(keyId=userId, refId=entityId)
        self._delCachedRelationship(userId)
        return result

    def getUserTodosEntities(self, userId):
        ### TODO: Add limit? Add timestamp to slice?
        try:
            return self._getCachedRelationship(userId)
        except KeyError:
            pass

        entityIds = self._getRelationships(userId)

        self._setCachedRelationship(userId, entityIds)

        return entityIds

