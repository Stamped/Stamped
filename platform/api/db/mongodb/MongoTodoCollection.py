#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, pymongo

from datetime                           import datetime
from utils                              import lazyProperty

from api.ATodoDB                            import ATodoDB
from api.db.mongodb.AMongoCollectionView               import AMongoCollectionView
from api.db.mongodb.MongoUserTodosEntitiesCollection   import MongoUserTodosEntitiesCollection
from api.db.mongodb.MongoUserTodosHistoryCollection    import MongoUserTodosHistoryCollection
from api.Schemas                        import *
from api.Entity                             import buildEntity

class MongoTodoCollection(AMongoCollectionView, ATodoDB):

    def __init__(self):
        AMongoCollectionView.__init__(self, collection='favorites', primary_key='todo_id', obj=RawTodo)
        ATodoDB.__init__(self)

        self._collection.ensure_index([('entity.entity_id', pymongo.ASCENDING),\
            ('user_id', pymongo.ASCENDING), ('_id', pymongo.DESCENDING)])

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
        entity = buildEntity(entityData, mini=True)
        document['entity'] = {'entity_id': entity.entity_id}

        stampData = document.pop('stamp', None)
        if stampData is not None:
            document['source_stamp_ids'] = [stampData['stamp_id']]

        rawtodo = self._obj().dataImport(document, overflow=self._overflow)
        rawtodo.entity = entity

        return rawtodo

    ### INTEGRITY

    def checkIntegrity(self, key, repair=False, api=None):
        """
        Check the raw todo to verify the following things:

        - Todo has the proper structure (updated schema)

        - Linked user exists

        - Linked entity exists and is not tombstoned 

        - Entity mini matches linked entity

        - If associated with a stamp, verify that the stamp still exists

        - Check if it's been stamped 

        """

        document = self._getMongoDocumentFromId(key)
        
        assert document is not None

        modified = False

        # Check if old schema version
        if 'stamp' in document:
            msg = "%s: Old schema" % key
            if repair:
                logs.info(msg)
                modified = True
            else:
                raise StampedDataError(msg)

        todo = self._convertFromMongo(document)

        # Verify that user exists
        userId = todo.user_id
        if self._collection._database['users'].find({'_id': self._getObjectIdFromString(userId)}).count() == 0:
            msg = "%s: User not found (%s)" % (key, userId)
            raise StampedDataError(msg)

        # Verify that entity exists
        entityId = todo.entity.entity_id
        entityDocument = self._collection._database['entities'].find_one({'_id' : self._getObjectIdFromString(entityId)})
        if entityDocument is None:
            msg = "%s: Entity not found (%s)" % (key, entityId)
            raise StampedDataError(msg)
        entity = buildEntity(entityDocument)

        # Check if entity has been tombstoned and update entity if so
        if entity.sources.tombstone_id is not None:
            msg = "%s: Entity tombstoned to new entity" % (key)
            if repair:
                logs.info(msg)
                tombstoneId = entity.sources.tombstone_id
                tombstone = self._collection._database['entities'].find_one({'_id' : self._getObjectIdFromString(tombstoneId)})
                if tombstone is None:
                    msg = "%s: New tombstone entity not found (%s)" % (key, tombstoneId)
                    raise StampedDataError(msg)
                todo.entity = buildEntity(tombstone).minimize()
                modified = True
            else:
                raise StampedDataError(msg)

        # Check if entity stub has been updated
        else:
            if todo.entity != entity.minimize():
                msg = "%s: Embedded entity is stale" % key
                if repair:
                    logs.info(msg)
                    todo.entity = entity.minimize()
                    modified = True
                else:
                    raise StampedDataError(msg)

        # Check if source stamps are still valid
        if todo.source_stamp_ids is not None:
            stampIds = []
            for stampId in todo.source_stamp_ids:
                query = {'_id': self._getObjectIdFromString(stampId)}
                if self._collection._database['stamps'].find(query).count() == 1:
                    stampIds.append(stampId)
                else:
                    msg = "%s: Sourced stamp not found (%s)" % (key, stampId)
                    if repair:
                        logs.info(msg)
                        modified = True
                    else:
                        raise StampedDataError(msg)
            if len(stampIds) > 0:
                todo.source_stamp_ids = stampIds 
            else:
                msg = "%s: Cleaning up source stamp ids" % key
                logs.info(msg)
                if repair:
                    del(todo.source_stamp_ids)
                    modified = True

        # Check if todo has been stamped and verify only one possible todo exists
        query = {'user.user_id': todo.user_id, 'entity.entity_id': todo.entity.entity_id}
        stamps = self._collection._database['stamps'].find(query, fields=['_id'])
        stampIds = map(lambda x: str(x['_id']), stamps)
        if len(stampIds) == 1:
            if todo.stamp_id is None or todo.stamp_id != stampIds[0]:
                msg = "%s: Replacing stamp id" % key
                if repair:
                    logs.info(msg)
                    todo.stamp_id = stampIds[0]
                    modified = True
                else:
                    raise StampedDataError(msg)
        elif len(stampIds) > 1:
            msg = "%s: Multiple stamps exist for user '%s' and entity '%s'" % (key, todo.user_id, todo.entity.entity_id)
            raise StampedDataError(msg)

        if modified and repair:
            self._collection.update({'_id' : key}, self._convertToMongo(todo))

        return True

    ### PUBLIC

    @lazyProperty
    def user_todo_entities_collection(self):
        return MongoUserTodosEntitiesCollection()

    @lazyProperty
    def user_todos_history_collection(self):
        return MongoUserTodosHistoryCollection()

    def addTodo(self, todo):
        todo = self._addObject(todo)

        # Add a reference to the todo in the user's 'todo' history collection
        self.user_todos_history_collection.addUserTodo(todo.user_id, todo.todo_id)

        # Add links to todo
        self.user_todo_entities_collection.addUserTodosEntity(\
            todo.user_id, todo.entity.entity_id)

        return todo

    def removeTodo(self, userId, entityId):
        try:
            self._collection.remove({'entity.entity_id': entityId,\
                                     'user_id': userId})

            # Remove links to todo
            self.user_todo_entities_collection.removeUserTodosEntity(\
                userId, entityId)
        except:
            logs.warning("Cannot remove document")
            raise Exception

    def getTodo(self, userId, entityId):
        document = self._collection.find_one({'entity.entity_id': entityId, 'user_id': userId})
        if document is None:
            raise StampedDocumentNotFoundError("Unable to find document (userId=%s, entityId=%s)" % (userId, entityId))
        todo = self._convertFromMongo(document)
        return todo

    def getTodos(self, userId, timeSlice):
        query = { 'user_id' : userId }

        return self._getTimeSlice(query, timeSlice)

    def getTodosFromStampId(self, stampId):
        documents = self._collection.find({ '$or': [{'source_stamp_ids' : stampId}, {'stamp.stamp_id': stampId}] }, fields=['user_id'])
        return map(lambda x: x['user_id'], documents)

    def countTodos(self, userId):
        n = self._collection.find({'user_id': userId}).count()
        return n

    def getTodoEntityIds(self, userId):
        return self.user_todo_entities_collection.getUserTodosEntities(userId)

    def getUserIdsFromEntityId(self, entityId, limit=10):
        ### TODO: Convert to index collection
        documents = self._collection.find({'entity.entity_id': entityId}, fields={'user_id': 1}).sort('$natural', pymongo.DESCENDING).limit(limit)
        return map(lambda x: x['user_id'], documents)

    def getTodoIdsFromEntityId(self, entityId, limit=0):
        documents = self._collection.find({'entity.entity_id': entityId}, fields={'_id': 1}).limit(limit)
        return map(lambda x: self._getStringFromObjectId(x['_id']), documents)

    def getTodosFromUsersForEntity(self, userIds, entityId, limit=10):
        ### TODO: Convert to index collection
        query = { 'entity.entity_id' : entityId, 'user_id' : { '$in' : userIds } }
        documents = self._collection.find(query, fields=['user_id']).limit(limit)
        return map(lambda x: x['user_id'], documents)

    def updateTodoEntity(self, todoId, entity):
        self._collection.update({'_id': self._getObjectIdFromString(todoId)}, {'$set': {'entity': entity.dataExport()}})

    def getUserTodosHistory(self, userId):
        return self.user_todos_history_collection.getUserTodos(userId)

    def removeUserTodosHistory(self, userId):
        return self.user_todos_history_collection.removeUserTodos(userId)

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

