#!/usr/bin/env python

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
    from Entity                         import setFields, isEqual, getSimplifiedTitle, upgradeEntityData, buildEntity

    from AMongoCollection               import AMongoCollection
    from MongoPlacesEntityCollection    import MongoPlacesEntityCollection
    from MongoMenuCollection            import MongoMenuCollection
    from AEntityDB                      import AEntityDB
    from difflib                        import SequenceMatcher
    from ADecorationDB                  import ADecorationDB
    from errors                         import StampedUnavailableError
    from logs                           import log
except:
    report()
    raise


class MongoEntityCollection(AMongoCollection, AEntityDB, ADecorationDB):
    
    def __init__(self, collection='entities'):
        AMongoCollection.__init__(self, collection=collection, primary_key='entity_id', overflow=True)
        AEntityDB.__init__(self)
    
    @lazyProperty
    def places_collection(self):
        return MongoPlacesEntityCollection()
    
    ### PUBLIC
    
    def _convertFromMongo(self, document):
        if document is None:
            return None

        if '_id' in document and self._primary_key is not None:
            document[self._primary_key] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])

        if 'schema_version' not in document:
            entity = upgradeEntityData(document)
        else:
            entity = buildEntity(document)
        
        if entity.title_lower is None:
            entity.title_lower = getSimplifiedTitle(entity.title)
        
        return entity
    
    def _convertToMongo(self, entity):
        if entity is not None and entity.title_lower is None:
            entity.title_lower = getSimplifiedTitle(entity.title)
        if entity.entity_id is not None and entity.entity_id.startswith('T_'):
            del entity.entity_id
        document = AMongoCollection._convertToMongo(self, entity)
        
        return document
    
    def addEntity(self, entity):
        if entity.title_lower is None:
            entity.title_lower = getSimplifiedTitle(entity.title)
        
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
            if entity.title_lower is None:
                entity.title_lower = getSimplifiedTitle(entity.title)
        
        return self._addObjects(entities)

    def updateDecoration(self, name, value):
        if name == 'menu':
            self.__menu_db.updateMenu(value)

