#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from AMongoCollection import AMongoCollection

class MongoUserTodoEntitiesCollection(AMongoCollection):

    def __init__(self):
        AMongoCollection.__init__(self, collection='userfaventities')

    ### PUBLIC

    def addUserTodoEntity(self, userId, entityId):
        self._createRelationship(keyId=userId, refId=entityId)
        return True

    def removeUserTodoEntity(self, userId, entityId):
        return self._removeRelationship(keyId=userId, refId=entityId)

    def getUserTodoEntities(self, userId):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(userId)

