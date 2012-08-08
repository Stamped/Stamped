#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from api_old.Schemas import *

import utils
import datetime
import time
import logs

from db.mongodb.MongoUserCollection import MongoUserCollection
from db.mongodb.MongoTodoCollection import MongoTodoCollection
from db.mongodb.MongoStampCollection import MongoStampCollection
from db.mongodb.MongoEntityCollection import MongoEntityCollection
from db.mongodb.MongoFriendshipCollection import MongoFriendshipCollection

from utils import lazyProperty, LoggingThreadPool

from api.module import APIObject
from api.stamps import Stamps
from api.activity import Activity
from api.accounts import Accounts
from api.entities import Entities


class Todos(APIObject):

    def __init__(self):
        APIObject.__init__(self)

    @lazyProperty
    def _userDB(self):
        return MongoUserCollection()

    @lazyProperty
    def _todoDB(self):
        return MongoTodoCollection()
    
    @lazyProperty
    def _stampDB(self):
        return MongoStampCollection()

    @lazyProperty
    def _entityDB(self):
        return MongoEntityCollection()

    @lazyProperty
    def _friendshipDB(self):
        return MongoFriendshipCollection()

    @lazyProperty
    def _stamps(self):
        return Stamps()

    @lazyProperty
    def _activity(self):
        return Activity()

    @lazyProperty
    def _accounts(self):
        return Accounts()

    @lazyProperty
    def _entities(self):
        return Entities()


    def _enrichTodoObjects(self, rawTodos, **kwargs):

        previewLength = kwargs.pop('previews', 10)

        authUserId  = kwargs.pop('authUserId', None)
        entityIds   = kwargs.pop('entityIds', {})
        stampIds    = kwargs.pop('stampIds', {})
        userIds     = kwargs.pop('userIds', {})

        singleTodo = False
        if not isinstance(rawTodos, list):
            singleTodo = True
            rawTodos = [rawTodos]

        """
        ENTITIES

        Enrich the underlying entity object for all todos
        """
        allEntityIds = set()

        for todo in rawTodos:
            allEntityIds.add(todo.entity.entity_id)

        # Enrich missing entity ids
        missingEntityIds = allEntityIds.difference(set(entityIds.keys()))
        entities = self._entityDB.getEntityMinis(list(missingEntityIds))

        for entity in entities:
            if entity.sources.tombstone_id is not None:
                # Convert to newer entity
                replacement = self._entityDB.getEntityMini(entity.sources.tombstone_id)
                entityIds[entity.entity_id] = replacement
                # Call async process to update references
                self.call_task(self.updateTombstonedEntityReferencesAsync, {'oldEntityId': entity.entity_id})
            else:
                entityIds[entity.entity_id] = entity

        """
        STAMPS

        Enrich the underlying stamp objects from sourced stamps or if the user has created a stamp
        """
        allStampIds  = set()

        for todo in rawTodos:
            if todo.stamp_id is not None:
                allStampIds.add(todo.stamp_id)
            if todo.source_stamp_ids is not None:
                for stampId in todo.source_stamp_ids:
                    allStampIds.add(stampId)

        # Enrich underlying stamp ids
        stamps = self._stampDB.getStamps(list(allStampIds))

        for stamp in stamps:
            stampIds[stamp.stamp_id] = stamp

        """
        USERS

        Enrich the underlying user objects. This includes:
        - To-do owner
        - Sourced stamps
        - Also to-do'd by
        """
        allUserIds    = set()

        # Add owner
        for todo in rawTodos:
            allUserIds.add(todo.user_id)

        # Add sourced stamps
        for stamp in stamps:
            allUserIds.add(stamp.user.user_id)

        # Add to-dos from friends if logged in
        friendTodos = {}
        if authUserId is not None:
            friendIds = self._friendshipDB.getFriends(authUserId)
            for todo in rawTodos:
                todoUserIds = self._todoDB.getTodosFromUsersForEntity(friendIds, todo.entity.entity_id, limit=10)
                if todoUserIds is not None and len(todoUserIds) > 0:
                    friendTodos[todo.todo_id] = todoUserIds
                    allUserIds = allUserIds.union(set(todoUserIds))

        # Enrich missing user ids
        missingUserIds = allUserIds.difference(set(userIds.keys()))
        users = self._userDB.lookupUsers(list(missingUserIds))

        for user in users:
            userIds[user.user_id] = user.minimize()

        """
        APPLY DATA
        """
        todos = []

        for todo in rawTodos:
            try:
                # User
                user = userIds[todo.user_id]
                if user is None:
                    logs.warning("%s: User not found (%s)" % (todo.todo_id, todo.user_id))
                    continue 

                # Entity
                entity = entityIds[todo.entity.entity_id]
                if entity is None:
                    logs.warning("%s: Entity not found (%s)" % (todo.todo_id, todo.entity.entity_id))

                # Source stamps
                sourceStamps = []
                if todo.source_stamp_ids is not None:
                    for stampId in todo.source_stamp_ids:
                        if stampId not in stampIds or stampIds[stampId] is None:
                            logs.warning("%s: Source stamp not found (%s)" % (todo.todo_id, stampId))
                            continue
                        sourceStamps.append(stampIds[stampId])

                # Stamp
                stamp = None 
                if todo.stamp_id is not None:
                    if todo.stamp_id not in stampIds or stampIds[todo.stamp_id] is None:
                        logs.warning("%s: Stamp not found (%s)" % (todo.todo_id, todo.stamp_id))
                    else:
                        stamp = stampIds[todo.stamp_id]

                # Also to-do'd by
                previews = None 
                if todo.todo_id in friendTodos and len(friendTodos[todo.todo_id]) > 0:
                    friends = []
                    for friendId in friendTodos[todo.todo_id]:
                        if friendId not in userIds or userIds[friendId] is None:
                            logs.warning("%s: Friend preview not found (%s)" % (todo.todo_id, friendId))
                            continue
                        friends.append(userIds[friendId])
                    if len(friends) > 0:
                        previews = Previews()
                        previews.todos = friends 

                todos.append(todo.enrich(user, entity, previews=previews, sourceStamps=sourceStamps, stamp=stamp))

            except KeyError, e:
                logs.warning("Fatal key error: %s" % e)
                logs.debug("Todo: %s" % todo)
                continue
            except Exception:
                raise

        if singleTodo:
            return todos[0]

        return todos

    def _enrichTodo(self, rawTodo, user=None, entity=None, sourceStamps=None, stamp=None, friendIds=None, authUserId=None):
        if user is None or user.user_id != rawTodo.user_id:
            user = self._userDB.getUser(rawTodo.user_id).minimize()

        if entity is None or entity.entity_id != rawTodo.entity.entity_id:
            entity = self._entityDB.getEntityMini(rawTodo.entity.entity_id)

        if sourceStamps is None and rawTodo.source_stamp_ids is not None:
            # Enrich stamps
            sourceStamps = self._stampDB.getStamps(rawTodo.source_stamp_ids)
            sourceStamps = self._stamps.enrichStampObjects(sourceStamps, entityIds={ entity.entity_id : entity }, authUserId=authUserId, mini=True)

        # If Stamp is completed, check if the user has stamped it to populate todo.stamp_id value.
        # this is necessary only for backward compatability.  The new RawTodo schema includes the stamp_id val
        if stamp is None and rawTodo.complete and rawTodo.stamp_id is None and authUserId:
            stamp = self._stampDB.getStampFromUserEntity(authUserId, entity.entity_id)
            if stamp is not None:
                rawTodo.stamp_id = stamp.stamp_id

        previews = None
        if friendIds is not None:
            previews = Previews()

            # TODO: We may want to optimize how we pull in followers' todos by adding a new ref collection as we do
            #  for likes on stamps.
            friendIds = self._todoDB.getTodosFromUsersForEntity(friendIds, entity.entity_id)
            users = self._userDB.lookupUsers(friendIds, limit=10)
            users =  map(lambda x: x.minimize(), users)
            previews.todos = users


        return rawTodo.enrich(user, entity, previews, sourceStamps, stamp)

    def addTodo(self, authUserId, entityRequest, stampId=None):
        # Entity
        entity = self._entities.getEntityFromRequest(entityRequest)

        todo                    = RawTodo()
        todo.entity             = entity.minimize()
        todo.user_id            = authUserId
        todo.timestamp          = BasicTimestamp()
        todo.timestamp.created  = datetime.datetime.utcnow()

        if stampId is not None:
            # Verify stamp exists
            try:
                source = self._stampDB.getStamp(stampId)
                todo.source_stamp_ids = [source.stamp_id]
            except StampedUnavailableError:
                stampId = None

        # Check to verify that user hasn't already todo'd entity
        try:
            return self._enrichTodoObjects(self._todoDB.getTodo(authUserId, entity.entity_id), authUserId=authUserId)
        except StampedUnavailableError:
            pass

        # Check if user has already stamped the todo entity, mark as complete and provide stamp_id, if so
        stamp = self._stampDB.getStampFromUserEntity(authUserId, entity.entity_id)
        if stamp is not None:
            todo.complete = True
            todo.stamp_id = stamp.stamp_id

        # Check if user has todoed the stamp previously; if so, don't send activity alerts
        previouslyTodoed = False
        history = self._todoDB.getUserTodosHistory(authUserId)
        if todo.todo_id in history:
            previouslyTodoed = True

        todo = self._todoDB.addTodo(todo)

        # Enrich todo
        todo = self._enrichTodoObjects(todo, authUserId=authUserId)

        # Call async process
        payload = {
            'authUserId': authUserId,
            'entityId': entity.entity_id,
            'stampId': stampId,
            'previouslyTodoed': previouslyTodoed,
        }
        self.call_task(self.addTodoAsync, payload)

        return todo

    def addTodoAsync(self, authUserId, entityId, stampId=None, previouslyTodoed=False):
        
        # Friends
        friendIds = self._friendshipDB.getFriends(authUserId)

        # Increment user stats by one
        self._userDB.updateUserStats(authUserId, 'num_todos', increment=1)

        # Add activity to all of your friends who stamped the entity
        stamps = self._stampDB.getStampsFromUsersForEntity(friendIds, entityId)

        # Stamp
        if stampId is not None:
            try:
                stamps.append(self._stampDB.getStamp(stampId))
            except StampedUnavailableError:
                logs.warning("Could not find stamp %s" % stampId)

        for stamp in stamps:

            # Send activity
            if authUserId != stamp.user.user_id and not previouslyTodoed:
                self._activity.addTodoActivity(authUserId, [stamp.user.user_id], entityId, stamp.stamp_id)

            # Update stamp stats
            self.call_task(self._stamps.updateStampStatsAsync, {'stampId': stamp.stamp_id})

        # Post to Facebook Open Graph if enabled
        # for now, we only post to OpenGraph if the todo was created off of a stamp
        if stampId is not None:
            share_settings = self._accounts.getOpenGraphShareSettings(authUserId)
            if share_settings is not None and share_settings.share_todos:
                self.call_task(self._stamps.postToOpenGraphAsync, {'authUserId': authUserId, 'todoStampId':stampId})

    def completeTodo(self, authUserId, entityId, complete):
        try:
            RawTodo = self._todoDB.getTodo(authUserId, entityId)
        except StampedUnavailableError:
            raise StampedTodoNotFoundError('Invalid todo: %s' % entityId)

        self._todoDB.completeTodo(entityId, authUserId, complete=complete)

        # Enrich todo
        RawTodo.complete = complete
        todo = self._enrichTodoObjects(RawTodo, authUserId=authUserId)

        # TODO: Add activity item

        #if todo.stamp is not None and todo.stamp.stamp_id is not None:
            # Remove activity
            #self._activityDB.removeActivity('todo', authUserId, stampId=todo.stamp.stamp_id)

        # Update stamp stats
#        if todo.sourceStamps is not None:
#            for stamp in todo.sourceStamps:
#                tasks.invoke(tasks.APITasks.updateStampStats, args=[stamp.stamp_id])

        return todo

    def removeTodo(self, authUserId, entityId):
        try:
            rawTodo = self._todoDB.getTodo(authUserId, entityId)
        except StampedUnavailableError:
            return True

        self._todoDB.removeTodo(authUserId, entityId)

        # Decrement user stats by one
        self._userDB.updateUserStats(authUserId, 'num_todos', increment=-1)

        if rawTodo.stamp_id is not None:
            self.call_task(self._stamps.updateStampStatsAsync, {'stampId': rawTodo.stamp_id})

        return True

    def getTodos(self, authUserId, timeSlice):

        if timeSlice.limit is None or timeSlice.limit <= 0 or timeSlice.limit > 50:
            timeSlice.limit = 50

        # Add one second to timeSlice.before to make the query inclusive of the timestamp passed
        if timeSlice.before is not None:
            timeSlice.before = timeSlice.before + datetime.timedelta(seconds=1)

        todos = self._todoDB.getTodos(authUserId, timeSlice)
        return self._enrichTodoObjects(todos, authUserId=authUserId)
 
    def getStampTodos(self, authUserId, stamp_id):
        return self._todoDB.getTodosFromStampId(stamp_id)
    
