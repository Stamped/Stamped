#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from utils import lazyProperty

from db.mongodb.MongoTodoCollection import MongoTodoCollection
from db.mongodb.MongoUserTodosEntitiesCollection import MongoUserTodosEntitiesCollection
from db.mongodb.MongoUserTodosHistoryCollection import MongoUserTodosHistoryCollection

class TodoDB(object):

    @lazyProperty
    def __todo_collection(self):
        return MongoStampCollection()

    @lazyProperty
    def __user_todos_entities_collection(self):
        return MongoUserTodosEntitiesCollection()

    @lazyProperty
    def __user_todos_history_collection(self):
        return MongoUserTodosHistoryCollection()


    def checkIntegrity(self, key, repair=False, api=None):
        return self.__todo_collection.checkIntegrity(key, repair=repair, api=api)


    def addTodo(self, todo):
        return self.__todo_collection.addTodo(todo)

    def removeTodo(self, userId, entityId):
        return self.__todo_collection.removeTodo(todo)

    def getTodo(self, userId, entityId):
        return self.__todo_collection.getTodo(userId, entityId)

    def getTodos(self, userId, timeSlice):
        return self.__todo_collection.getTodos(userId, timeSlice)

    def getTodosFromStampId(self, stampId):
        return self.__todo_collection.getTodosFromStampId(stampId)

    def countTodos(self, userId):
        return self.__todo_collection.countTodos(userId)

    def getTodoEntityIds(self, userId):
        return self.__user_todos_entities_collection.getUserTodosEntities(userId)

    def getUserIdsFromEntityId(self, entityId, limit=10):
        return self.__todo_collection.getUserIdsFromEntityId(entityId, limit=limit)

    def getTodoIdsFromEntityId(self, entityId, limit=0):
        return self.__todo_collection.getTodoIdsFromEntityId(entityId, limit=limit)

    def countTodosFromEntityId(self, entityId):
        return self.__todo_collection.countTodosFromEntityId(entityId)

    def getTodosFromUsersForEntity(self, userIds, entityId, limit=10):
        return self.__todo_collection.getTodosFromUsersForEntity(userIds, entityId, limit=limit)

    def updateTodoEntity(self, todoId, entity):
        return self.__todo_collection.updateTodoEntity(todoId, entity)

    def getUserTodosHistory(self, userId):
        return self.__user_todos_history_collection.getUserTodos(userId)

    def removeUserTodosHistory(self, userId):
        return self.__user_todos_history_collection.removeUserTodos(userId)

    def completeTodo(self, entityId, userId, complete=True):
        return self.__todo_collection.completeTodo(entityId, userId, complete=complete)
