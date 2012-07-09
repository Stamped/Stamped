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
    from api.Entity                         import getSimplifiedTitle, buildEntity

    from api.db.mongodb.AMongoCollection               import AMongoCollection
    from api.db.mongodb.MongoPlacesEntityCollection    import MongoPlacesEntityCollection
    from api.db.mongodb.MongoEntitySeedCollection      import MongoEntitySeedCollection
    from api.db.mongodb.MongoMenuCollection            import MongoMenuCollection
    from api.AEntityDB                      import AEntityDB
    from difflib                        import SequenceMatcher
    from api.ADecorationDB                  import ADecorationDB
    from errors                         import StampedUnavailableError
    from logs                           import log
except:
    report()
    raise


class MongoEntityCollection(AMongoCollection, AEntityDB, ADecorationDB):

    def __init__(self, collection='entities'):
        AMongoCollection.__init__(self, collection=collection, primary_key='entity_id', overflow=True)
        AEntityDB.__init__(self)

        fast_resolve_fields = ('sources.amazon_id', 'sources.spotify_id', 'sources.rdio_id',
                'sources.opentable_id', 'sources.tmdb_id', 'sources.factual_id',
                'sources.instagram_id', 'sources.singleplatform_id', 'sources.foursquare_id',
                'sources.fandango_id', 'sources.googleplaces_id', 'sources.itunes_id',
                'sources.netflix_id', 'sources.thetvdb_id')
        for field in fast_resolve_fields:
            self._collection.ensure_index(field)

    @lazyProperty
    def places_collection(self):
        return MongoPlacesEntityCollection()

    @lazyProperty
    def seed_collection(self):
        return MongoEntitySeedCollection()

    def _convertFromMongo(self, document, mini=False):
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

        entity = buildEntity(document, mini=mini)

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

    def getEntityMini(self, entityId):
        documentId  = self._getObjectIdFromString(entityId)
        params = {'_id' : documentId}
        fields = {'details.artist' : 0, 'tracks' : 0, 'albums' : 0, 'cast' : 0, 'desc' : 0  }

        documents = self._collection.find(params, fields)
        if documents.count() == 0:
            raise StampedDocumentNotFoundError("Unable to find entity (id = %s)" % documentId)
        entity = self._convertFromMongo(documents[0])
        entity = entity.minimize()

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

    def getEntityMinis(self, entityIds):
        documentIds = []
        for entityId in entityIds:
            documentIds.append(self._getObjectIdFromString(entityId))
        params = {'_id': {'$in': documentIds}}
        fields = {'details.artist' : 0, 'tracks' : 0, 'albums' : 0, 'cast' : 0, 'desc' : 0  }

        documents = self._collection.find(params, fields)

        result = []
        for doc in documents:
            entity = self._convertFromMongo(doc, mini=False)
            entity = entity.minimize()
            # if entity.tombstone_id is not None:
            #     entity = self.getEntity(entity.tombstone_id)
            result.append(entity)

        return result

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

    def getEntitiesByQuery(self, queryDict):
        return (self._convertFromMongo(item) for item in self._collection.find(queryDict))

    def updateEntity(self, entity):
        document = self._convertToMongo(entity)
        document = self._updateMongoDocument(document)

        return self._convertFromMongo(document)

    def removeEntity(self, entityId):
        documentId = self._getObjectIdFromString(entityId)
        return self._removeMongoDocument(documentId)

    def removeCustomEntity(self, entityId, userId):
        try:
            query = {'_id': self._getObjectIdFromString(entityId), 'sources.user_generated_id': userId}
            self._collection.remove(query)
            query = {'_id': self._getObjectIdFromString(entityId), 'sources.userGenerated.user_id': userId} # Deprecated version
            self._collection.remove(query)
            return True
        except Exception:
            logs.warning("Cannot remove custom entity")
            raise

    def addEntities(self, entities):
        return self._addObjects(entities)

    def updateDecoration(self, name, value):
        if name == 'menu':
            self.__menu_db.updateMenu(value)

