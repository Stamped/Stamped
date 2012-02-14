#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs       import report

try:
    from datetime                       import datetime
    from utils                          import lazyProperty

    from Schemas                        import *
    from Entity                         import setFields, isEqual, getSimplifiedTitle

    from AMongoCollection               import AMongoCollection
    from MongoPlacesEntityCollection    import MongoPlacesEntityCollection
    from MongoMenuCollection            import MongoMenuCollection
    from AEntityDB                      import AEntityDB
    from difflib                        import SequenceMatcher
    from libs.Factual                   import Factual
    from libs.FactualSource             import FactualSource
    from libs.GooglePlacesSource        import GooglePlacesSource
    from libs.SinglePlatformSource      import SinglePlatformSource
    from libs.ExternalSourceController  import ExternalSourceController
    from ADecorationDB                  import ADecorationDB
    from errors                         import StampedUnavailableError
except:
    report()
    raise

_menu_sources = {
    'singleplatform':'singleplatform_id',
}

class MongoEntityCollection(AMongoCollection, AEntityDB, ADecorationDB):
    
    def __init__(self, collection='entities'):
        AMongoCollection.__init__(self, collection=collection, primary_key='entity_id', obj=Entity)
        AEntityDB.__init__(self)
    
    @lazyProperty
    def places_collection(self):
        return MongoPlacesEntityCollection()

    @lazyProperty
    def __menu_db(self):
        return MongoMenuCollection()

    @lazyProperty
    def factual(self):
        return Factual()
    
    @lazyProperty
    def __factual(self):
        return FactualSource()

    @lazyProperty
    def __googleplaces(self):
        return GooglePlacesSource()

    @lazyProperty
    def __singleplatform(self):
        return SinglePlatformSource()

    @lazyProperty
    def __controller(self):
        return ExternalSourceController()
    
    @lazyProperty
    def __sources(self):
        return [self.__factual,self.__googleplaces,self.__singleplatform]
    
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
    
    def enrichEntity(self, entity, resolve=True, enrich=True, decorate=True):
        self.__controller.clearNow()
        update_required = False
        if resolve:
            for source in self.__sources:
                try:
                    modified = source.resolveEntity(entity, self.__controller)
                    update_required |= modified
                except:
                    report("Unexpected resolve error from %s",source.sourceName)
        if enrich:
            for source in self.__sources:
                try:
                    modified = source.enrichEntity(entity, self.__controller)
                    update_required |= modified
                except:
                    report("Unexpected enrich error from %s",source.sourceName)
        if decorate:
            for source in self.__sources:
                try:
                    modified = source.decorateEntity(entity, self.__controller, self)
                    update_required |= modified
                except:
                    report("Unexpected decorate error from %s",source.sourceName)
        return update_required

    def getMenu(self, entityId):
        menu = self.__menu_db.getMenu(entityId)
        if menu is None:
            entity = self.getEntity(entityId)
            modified = self.enrichEntity(entity)
            if modified:
                self.updateEntity(entity)
            menu = self.__menu_db.getMenu(entityId)
        if menu is None:
            raise StampedUnavailableError("Unable to find menu (id = %s)" % entityId)
        return menu
    
    def updateEntity(self, entity):
        document = self._convertToMongo(entity)
        document = self._updateMongoDocument(document)
        
        return self._convertFromMongo(document)
    
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

    def updateDecoration(self, name, value):
        if name == 'menu':
            self.__menu_db.updateMenu(value)
        
