#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from api.db.mongodb.AMongoCollection import AMongoCollection

class MongoUserTodosEntitiesCollection(AMongoCollection):

    def __init__(self):
        AMongoCollection.__init__(self, collection='userfaventities')

    """
    User Id -> Entity Ids 
    """

    ### INTEGRITY

    def checkIntegrity(self, key, noop=False):

        def regenerate(key):
            entityIds = set()
            todos = self._collection._database['favorites'].find({'user_id': key}, fields=['entity.entity_id'])
            for todo in todos:
                entityIds.add(str(todo['entity']['entity_id']))

            return { '_id' : key, 'ref_ids' : list(entityIds) }

        def keyCheck(key):
            assert self._collection._database['users'].find({'_id': self._getObjectIdFromString(key)}).count() == 1

        return self._checkRelationshipIntegrity(key, keyCheck, regenerate, noop=noop)

    ### PUBLIC

    def addUserTodosEntity(self, userId, entityId):
        self._createRelationship(keyId=userId, refId=entityId)
        return True

    def removeUserTodosEntity(self, userId, entityId):
        return self._removeRelationship(keyId=userId, refId=entityId)

    def getUserTodosEntities(self, userId):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(userId)

