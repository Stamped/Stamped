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
    from bson.objectid                  import ObjectId

    from api.Schemas                        import *
    from Entity                         import getSimplifiedTitle, buildEntity

    from AMongoCollection               import AMongoCollection
    from MongoPlacesEntityCollection    import MongoPlacesEntityCollection
    from MongoEntitySeedCollection      import MongoEntitySeedCollection
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
    
    @lazyProperty
    def seed_collection(self):
        return MongoEntitySeedCollection()
    
    def _convertFromMongo(self, document):
        if document is None:
            return None

        if '_id' in document and self._primary_key is not None:
            document[self._primary_key] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])

        ### HACK: Verify that 'created' timestamp exists for entity
        if 'timestamp' not in document or 'created' not in document['timestamp']:
            try:
                created = ObjectId(document[self._primary_key]).generation_time.replace(tzinfo=None)
            except:
                report()
                raise
            document['timestamp'] = { 'created' : created }

        document.pop('titlel')

        entity = buildEntity(document)

        return entity
    
    def _convertToMongo(self, entity):
        if entity.entity_id is not None and entity.entity_id.startswith('T_'):
            del entity.entity_id
        document = AMongoCollection._convertToMongo(self, entity)
        if document is None:
            return None
        if 'title' in document:
            document['titlel'] = getSimplifiedTitle(document['title'])
        return document
    
    ### PUBLIC
    
    def addEntity(self, entity):
        entity = self._addObject(entity)
        self.seed_collection.addEntity(entity)
        return entity
    
    def getEntity(self, entityId):
        documentId  = self._getObjectIdFromString(entityId)
        document    = self._getMongoDocumentFromId(documentId)
        entity      = self._convertFromMongo(document)
        
        # if entity.tombstone_id is not None:
        #     documentId  = self._getObjectIdFromString(entity.tombstone_id)
        #     document    = self._getMongoDocumentFromId(documentId)
        #     entity      = self._convertFromMongo(document)

        return entity
    
    def getEntities(self, entityIds):
        documentIds = []
        for entityId in entityIds:
            documentIds.append(self._getObjectIdFromString(entityId))
        data = self._getMongoDocumentsFromIds(documentIds)
        
        result = []
        for item in data:
            entity = self._convertFromMongo(item)
            # if entity.tombstone_id is not None:
            #     entity = self.getEntity(entity.tombstone_id)
            result.append(entity)
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
        return self._addObjects(entities)

    def updateDecoration(self, name, value):
        if name == 'menu':
            self.__menu_db.updateMenu(value)

