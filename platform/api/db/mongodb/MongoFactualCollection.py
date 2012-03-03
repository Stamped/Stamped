#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, logs, time

from datetime import datetime
from utils import lazyProperty
from Schemas import *

from AMongoCollection import AMongoCollection

from libs.Factual import Factual
from api.AFactualDB import AFactualDB
import datetime


from urllib2             import HTTPError
import tasks.APITasks
import tasks
import pprint

_refresh_days = 14

class MongoFactualCollection(AMongoCollection, AFactualDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='menus', primary_key='factual_id', obj=None)
        AFactualDB.__init__(self)
        self._collection.ensure_index('entity_id')

    @lazyProperty
    def __factual(self):
        return Factual()

    def __data(self, entity):
        mongo_id =self._getObjectIdFromString( entity.entity_id )
        doc = self._collection.find_one(mongo_id)
        result = None
        if doc is not None:
            result = self._convertFromMongo( doc )
        return result

    def __remove(self, entity):
        mongo_id =self._getObjectIdFromString( entity.entity_id )
        self._removeMongoDocument( mongo_id )

    ### PUBLIC

    def factual_data(self, entity):
        self.factual_update(entity)
        return self.__data(entity)
        
    def factual_update(self, entity, force_update=False, force_resolve=False, force_enrich=False):
        """
        Use Factual to enrich the given entity if necessary or forced.

        Returns a boolean indicating whether the given entity was modified.

        When set, force_update ensures that the factual data will be refreshed the Factual, not the local cache.

        When set, force_resolve ensures that the factual_id of the entity will be resolved (possibly overwriting the current value)

        When set, force_enrich ensures that the entity will be enriched regardless of whether it appears to need to be updated.
        """
        result = False
        force_update |= self.stale(entity)
        data = None
        timestamp = None
        if force_resolve or self.stale(entity):
            factual_id = self.__factual.factual_from_entity(entity)
            if factual_id != entity.factual_id:
                if factual_id == None:
                    self.__remove(entity)
                else:
                    force_enrich = True
                entity.factual_id = entity
                result = True
                force_update = True
        if force_update and entity.factual_id is not None:
            result = True
            data = self.__factual.data(entity.factual_id,entity=entity)
            if data is not None:
                force_enrich = True
                data['entity_id'] = entity.entity_id
                data['timestamp'] = datetime.utcnow()
                self.update(data)
            else:
                logs.warning("no data found for factual %s; ensuring removal of Factual data for entity %s" % ( entity.factual_id, entity.entity_id) )
                self.__remove( entity )
        if force_enrich and entity.factual_id is not None:
            if data is None:
                data = self.__data( entity )
            enriched = self.__factual.enrich(entity,data=data)
            if enriched and data is not None:
                timestamp = data['timestamp']
            result = result or enriched
        if result:
            if timestamp is None:
                timestamp = datetime.utcnow()
            entity.factual_timestamp = timestamp
        return result
    
    def stale(self,entity):
        """
        Indicates whether the entity appears to contain stale Factual data or none at all.
        """
        if 'factual_timestamp' not in entity:
            return True
        else:
            timestamp = entity.factual_timestamp
            now = datetime.utcnow()
            delta = now - timestamp
            if delta.days > _refresh_days:
                return True
            else:
                return False
