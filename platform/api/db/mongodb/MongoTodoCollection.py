#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, pymongo

from datetime                           import datetime
from utils                              import lazyProperty

from ATodoDB                            import ATodoDB
from AMongoCollectionView               import AMongoCollectionView
from MongoUserTodoEntitiesCollection    import MongoUserTodoEntitiesCollection
from api.Schemas                        import *
from Entity                             import buildEntity

class MongoTodoCollection(AMongoCollectionView, ATodoDB):

    def __init__(self):
        AMongoCollectionView.__init__(self, collection='favorites', primary_key='favorite_id', obj=RawTodo)
        ATodoDB.__init__(self)

        self._collection.ensure_index([('entity.entity_id', pymongo.ASCENDING),\
            ('user_id', pymongo.ASCENDING)])

        self._collection.ensure_index([('user_id', pymongo.ASCENDING),\
            ('timestamp.created', pymongo.DESCENDING)])

    def _convertFromMongo(self, document):
        """
        Keep in mind this is returning a RawTodo, which is less-enriched than a Todo
        """
        if document is None:
            return None

        if '_id' in document and self._primary_key is not None:
            document[self._primary_key] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])

        entityData = document.pop('entity')
        entity = buildEntity(entityData)
        document['entity'] = {'entity_id': entity.entity_id}

        stampData = document.pop('stamp', None)
        if stampData is not None:
            document['source_stamp_ids'] = [stampData['stamp_id']]

        if 'favorite_id' in document:
            document['todo_id'] = document['favorite_id']
            del(document['favorite_id'])

        rawtodo = self._obj().dataImport(document, overflow=self._overflow)
        rawtodo.entity = entity

        return rawtodo

    ### PUBLIC

    @lazyProperty
    def user_todo_entities_collection(self):
        return MongoUserTodoEntitiesCollection()

    def addTodo(self, todo):
        todo = self._addObject(todo)

        # Add links to todo
        self.user_todo_entities_collection.addUserTodoEntity(\
            todo.user_id, todo.entity.entity_id)

        return todo

    def removeTodo(self, userId, entityId):
        try:
            self._collection.remove({'entity.entity_id': entityId,\
                                     'user_id': userId})

            # Remove links to todo
            self.user_todo_entities_collection.removeUserTodoEntity(\
                userId, entityId)
        except:
            logs.warning("Cannot remove document")
            raise Exception

    def getTodo(self, userId, entityId):
        try:
            document = self._collection.find_one(\
                    {'entity.entity_id': entityId, 'user_id': userId})
            todo = self._convertFromMongo(document)
            return todo
        except:
            logs.warning("Cannot get document")
            raise Exception

    def getTodos(self, userId, genericCollectionSlice):
        query = { 'user_id' : userId }

        return self._getSlice(query, genericCollectionSlice)

    def countTodos(self, userId):
        n = self._collection.find({'user_id': userId}).count()
        return n

    def getTodoEntityIds(self, userId):
        return self.user_todo_entities_collection.getUserTodoEntities(userId)

    def getTodosFromEntityId(self, entityId, limit=10):
        ### TODO: Convert to index collection
        documents = self._collection.find({'entity.entity_id': entityId}, fields={'user_id': 1}).sort('$natural', pymongo.DESCENDING).limit(limit)
        return map(lambda x: x['user_id'], documents)

    def getTodosFromUsersForEntity(self, userIds, entityId, limit=10):
        ### TODO: Convert to index collection
        query = { 'entity.entity_id' : entityId, 'user_id' : { '$in' : userIds } }
        documents = self._collection.find(query, fields=['user_id']).sort('$natural', pymongo.DESCENDING).limit(limit)
        return map(lambda x: x['user_id'], documents)

    def completeTodo(self, entityId, userId, complete=True):
        try:
            self._collection.update(
                    {'entity.entity_id': entityId, 'user_id': userId},
                    {'$set': {'complete': complete}},
                safe=True
            )
        except:
            logs.warning("Cannot complete todo")
            raise Exception

