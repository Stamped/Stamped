#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from AMongoCollection import AMongoCollection

class MongoUserTodosEntitiesCollection(AMongoCollection):

    def __init__(self):
        AMongoCollection.__init__(self, collection='userfaventities')

    ### PUBLIC

    def addUserTodosEntity(self, userId, entityId):
        self._createRelationship(keyId=userId, refId=entityId)
        return True

    def removeUserTodosEntity(self, userId, entityId):
        return self._removeRelationship(keyId=userId, refId=entityId)

    def getUserTodosEntities(self, userId):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(userId)

