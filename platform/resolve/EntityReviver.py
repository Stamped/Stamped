#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = ['revive_tombstoned_entities']

import Globals
import logs
from libs.type_checking import *
from api.db.mongodb import MongoEntityCollection, MongoStampCollection, MongoTodoCollection
from api.MongoStampedAPI import globalMongoStampedAPI

@arg('entity_id', basestring, 'The id of the canonical entity')
def revive_tombstoned_entities(entity_id):
    """
    Finds all entities that are tombstoned to the given entity, undo the tombstone. This function will also find all
    stamps and todos that were transfered to the given entity as a consequence of tombstoning, and return those items to
    the original entity.
    """

    entities_by_id = {}
    entity_db = MongoEntityCollection.MongoEntityCollection()
    for entity in entity_db.getEntitiesByTombstoneId(entity_id):
        clear_tombstone_id(entity, entity_db, entities_by_id)

    todo_db = MongoTodoCollection.MongoTodoCollection()
    todo_seed_db = MongoTodoCollection.MongoSeedTodoCollection()
    for todo_id in todo_db.getTodoIdsFromEntityId(entity_id):
        original_entity_id = todo_seed_db.getEntityIdForTodo(todo_id)
        if original_entity_id is None:
            logs.warn('Could not find entity for seed todo: ' + todo_id)
            continue
        if original_entity_id in entities_by_id:
            entity = entities_by_id[original_entity_id]
        else:
            entity = entity_db.getEntity(original_entity_id)
            entity = clear_tombstone_id(entity, entity_db, entities_by_id)
        todo_db.updateTodoEntity(todo_id, entity.minimize())

    stamp_db = MongoStampCollection.MongoStampCollection()
    stamp_seed_db = MongoStampCollection.MongoSeedStampCollection()
    for stamp_id in stamp_db.getStampIdsForEntity(entity_id):
        original_entity_id = stamp_seed_db.getStamp(stamp_id).entity.entity_id
        if original_entity_id in entities_by_id:
            entity = entities_by_id[original_entity_id]
        else:
            entity = entity_db.getEntity(original_entity_id)
            entity = clear_tombstone_id(entity, entity_db, entities_by_id)
        stamp_db.updateStampEntity(stamp_id, entity.minimize())

    api = globalMongoStampedAPI()
    for entity in entities_by_id.itervalues():
        api.mergeEntity(entity)


def clear_tombstone_id(entity, entity_db, entity_cache):
    """
    Clears out all tombstone related field on the entity and persist it into the entity_db. Also save the entity in the
    cache.
    """
    if entity.entity_id not in entity_cache:
        del entity.sources.tombstone_id
        del entity.sources.tombstone_source
        del entity.sources.tombstone_timestamp
        entity_cache[entity.entity_id] = entity_db.updateEntity(entity)
    return entity

