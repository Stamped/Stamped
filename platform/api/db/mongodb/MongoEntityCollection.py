#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from datetime import datetime
from utils import lazyProperty

from Schemas import *
from Entity  import setFields, isEqual, getSimplifiedTitle

from AMongoCollection import AMongoCollection
from MongoPlacesEntityCollection import MongoPlacesEntityCollection
from MongoMenuCollection import MongoMenuCollection
from AEntityDB import AEntityDB
from difflib import SequenceMatcher
from libs.Factual import Factual

_menu_sources = {
    'singleplatform':'singleplatform_id',
}

class MongoEntityCollection(AMongoCollection, AEntityDB):
    
    def __init__(self, collection='entities'):
        AMongoCollection.__init__(self, collection=collection, primary_key='entity_id', obj=Entity)
        AEntityDB.__init__(self)
    
    @lazyProperty
    def places_collection(self):
        return MongoPlacesEntityCollection()

    @lazyProperty
    def menu_collection(self):
        return MongoMenuCollection()

    @lazyProperty
    def factual(self):
        return Factual()
    
    ### PUBLIC
    
    def _convertFromMongo(self, document):
        entity = AMongoCollection._convertFromMongo(self, document)
        if entity is not None and entity.titlel is None:
            entity.titlel = getSimplifiedTitle(entity.title)
        
        return entity
    
    def addEntity(self, entity):
        if entity.titlel is None:
            entity.titlel = getSimplifiedTitle(entity.title)
        
        return self._addObject(entity)
    
    def getEntity(self, entityId):
        documentId = self._getObjectIdFromString(entityId)
        document   = self._getMongoDocumentFromId(documentId)
        
        return self._convertFromMongo(document)
    
    def getEntities(self, entityIds):
        documentIds = []
        for entityId in entityIds:
            documentIds.append(self._getObjectIdFromString(entityId))
        data = self._getMongoDocumentsFromIds(documentIds)
        
        result = []
        for item in data:
            result.append(self._convertFromMongo(item))
        return result
    
    def getMenus(self, entityId):
        #logs.warning("getting menus for %s",entityId)
        menus = self.menu_collection.getMenus(entityId)
        if len(menus) == 0:
            entity = self.getEntity(entityId)
            if entity:
                #logs.warning("no menu found for %s" % entity.title)
                if 'factual_id' not in entity:
                    #logs.warning("looking for factual_id")
                    self.factual.enrich(entity)
                    if entity.factual_id is not None:
                        #logs.warning("factual_id is %s" % entity.factual_id)
                        self.updateEntity(entity)
                    else:
                        logs.warning("no factual_id found for %s" % entityId)
                if 'singleplatform_id' in entity:
                    #logs.warning("singleplatform_id is %s" % entity.singleplatform_id)
                    menu = self.updateMenu(entityId,'singleplatform',entity.singleplatform_id)
                    if menu is not None:
                        #logs.warning("adding menu for %s" % entity.singleplatform_id)
                        menus.append(menu)
        return menus

    def getMenu(self, entityId):
        menus = self.getMenus(entityId)
        menu = None
        for m in menus:
            if menu == None:
                menu = m
            elif m.quality > menu.quality:
                menu = m
        return menu
    
    def updateEntity(self, entity):
        document = self._convertToMongo(entity)
        document = self._updateMongoDocument(document)
        
        return self._convertFromMongo(document)
    
    def updateMenu(self, entityId, source, sourceId):
        return self.menu_collection.updateMenu(entityId,source,sourceId)
    
    def updateMenus(self, entityId):
        entity = self.getEntity(entityId)
        if entity is not None:
            for k,v in _menu_sources.items():
                if v in entity:
                    self.updateMenu(entityId,k,v)
    
    def removeEntity(self, entityId):
        documentId = self._getObjectIdFromString(entityId)
        return self._removeMongoDocument(documentId)
    
    def removeCustomEntity(self, entityId, userId):
        try:
            query = {'_id': self._getObjectIdFromString(entityId), \
                        'sources.userGenerated.user_id': userId}
            self._collection.remove(query)
            return True
        except:
            logs.warning("Cannot remove document")
            raise Exception
    
    def addEntities(self, entities):
        for entity in entities:
            if entity.titlel is None:
                entity.titlel = getSimplifiedTitle(entity.title)
        
        return self._addObjects(entities)

