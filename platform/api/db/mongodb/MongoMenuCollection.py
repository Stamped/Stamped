#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, logs, time

from datetime import datetime
from utils import lazyProperty
from Schemas import *

from AMongoCollection import AMongoCollection

from api.AMenuDB import AMenuDB

from libs.SinglePlatform import StampedSinglePlatform

from urllib2             import HTTPError
import tasks.APITasks
import tasks
import pprint

_refresh_days = 14

class MongoMenuCollection(AMongoCollection, AMenuDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='menus', primary_key=None, obj=MenuSchema)
        AMenuDB.__init__(self)

        self._collection.ensure_index('entity_id')
        self._collection.ensure_index('source_id')
        self._collection.ensure_index('source')
    
    @lazyProperty
    def __singleplatform(self):
        return StampedSinglePlatform()

    ### PUBLIC
    def getMenus(self, entityId):
        documents = self._collection.find({'entity_id': entityId})
        #logs.debug("\n\nFound %d %s menus\n\n"  % ( documents.count() , entityId ))
        menus = []
        cur = datetime.utcnow()
        for document in documents:
            #logs.debug("\n\nMenu found\n\n" )
            del document['_id']
            menu = self._convertFromMongo(document)
            age = cur - menu.timestamp
            if age.days > _refresh_days:
                tasks.invoke(tasks.APITasks._updateMenu, args=[entity_id,menu.source,menu.source_id])
            menus.append(menu)
        # TODO synchronous fallback
        return menus
    
    def updateMenu(self, entity_id, source, source_id):
        updated_menu = None
        if source == 'singleplatform':
            try:
                updated_menu = self.__singleplatform.get_menu_schema(source_id)
                if updated_menu is not None:
                    updated_menu.entity_id = entity_id
                    updated_menu.timestamp = datetime.utcnow()
            except HTTPError as e:
                logs.warning("Got an HTTP exception #%d for %s" % (e.code,source_id))
        if updated_menu is not None:
            #logs.warning("\n\nADDED Menu for %s" % updated_menu.source_id )
            mongo_obj = self._convertToMongo(updated_menu)
            #logs.warning("updated menu for %s:%s:%s\n%s" % (entity_id, source, source_id,pprint.pformat(updated_menu.value)))
            mongo_id = self._collection.insert_one(mongo_obj, safe=True)
            #assert self._collection.find({'entity_id':entity_id}).count() > 0
            #logs.warning("\nThere are now %d menus" % self._collection.find({'entity_id':entity_id}).count() )
            #logs.warning("added menu with _id %s" % mongo_id )
            self._collection.remove({'source':source,'source_id':source_id,'entity_id':entity_id,'_id':{ '$ne' : mongo_id }})
        return updated_menu
