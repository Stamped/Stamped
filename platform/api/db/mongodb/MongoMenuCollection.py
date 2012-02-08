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
import datetime

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
    def singleplatform(self):
        return StampedSinglePlatform()

    ### PUBLIC
    def getMenus(self, entityId):
        documents = self._collection.find({'enitity_id': entityId},output=list)
        menus = []
        cur = datetime.datetime.utcnow()
        for document in documents:
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
                updated_menu = self.singleplatform.get_menu_schema(source_id)
                updated_menu.entity_id = entity_id
            except HTTPError as e:
                logs.warning("Got an HTTP exception #%d" % (e.code,))

        if updated_menu is not None:
            logs.warning("updated menu for %s:%s:%s\n%s" % (entity_id, source, source_id,pprint.pformat(updated_menu.value)))
            mongo_id = self._collection.insert_one(updated_menu.value, safe=True)
            #self._collection.remove({'source':source,'source_id':source_id,'entity_id':entity_id,'_id':{ '$ne' : mongo_id }})
        return updated_menu
