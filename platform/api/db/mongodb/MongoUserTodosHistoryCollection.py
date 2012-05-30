#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from AMongoCollection import AMongoCollection

class MongoUserTodosHistoryCollection(AMongoCollection):

    def __init__(self):
        AMongoCollection.__init__(self, collection='usertodoshistory')

    ### PUBLIC

    def addUserTodo(self, userId, todoId):
        self._createRelationship(keyId=userId, refId=todoId)
        return True

    def getUserTodos(self, userId, limit=None):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(userId, limit)

    def removeUserTodos(self, userId):
        return self._removeAllRelationships(userId)