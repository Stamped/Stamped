#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs       import report

try:
    from datetime                       import datetime
    from utils                          import lazyProperty, getHeadRequest, getWebImageSize
    from bson.objectid                  import ObjectId

    from api.Schemas                        import *
    from api.Entity                         import getSimplifiedTitle, buildEntity

    from api.db.mongodb.AMongoCollection               import AMongoCollection
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
        self._collection.ensure_index('titlel')
        self._collection.ensure_index('albums.title')
        self._collection.ensure_index('artists.title')
        self._collection.ensure_index('authors.title')
        self._collection.ensure_index('tracks.title')

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

    ### INTEGRITY

    def checkIntegrity(self, key, repair=True):
        """
        Check the entity to verify the following things:

        - Entity has the proper structure (updated schema)

        - Populate third_party_ids if missing

        - If tombstoned, verify that tombstone points to a non-tombstoned / non-user-generated entity

        - If an image url exists, verify via a HEAD request that the image is valid

        - Source-specific assertions:
            - itunes_url exists if itunes_id exists
            - googleplaces_reference exists if googleplaces_id exists

        - If 'menu' is True, verify a menu exists

        """
        
        document = self._getMongoDocumentFromId(key)

        modified = False

        # Check if old schema version
        if 'schema_version' not in document:
            msg = "%s: Old schema" % key
            if repair:
                logs.info(msg)
                modified = True
            else:
                raise StampedDataError(msg)

        entity = self._convertFromMongo(document)

        # Verify tombstone is set properly
        if entity.sources.tombstone_id is not None:
            tombstone = None

            # Verify tombstoned entity still exists
            try:
                tombstone = self._getMongoDocumentFromId(self._getObjectIdFromString(entity.sources.tombstone_id))
                tombstone = self._convertFromMongo(tombstone)
            except StampedDocumentNotFoundError:
                msg = "%s: Tombstoned entity not found" % key
                if repair:
                    logs.info(msg)
                    del(entity.sources.tombstone_id)
                    del(entity.sources.tombstone_source)
                    del(entity.sources.tombstone_timestamp)
                else:
                    raise StampedDataError(msg)

            # Raise exception if tombstone is chained
            if tombstone is not None and tombstone.sources.tombstone_id is not None:
                if tombstone.sources.tombstone_id == entity.entity_id:
                    raise StampedTombstoneError("Entities tombstoned to each other: '%s' and '%s'" % \
                        (entity.entity_id, tombstone.entity_id))
                raise StampedTombstoneError("Entity tombstone chain: '%s' to '%s' to '%s'" % \
                    (entity.entity_id, tombstone.entity_id, tombstone.sources.tombstone_id))
                
            # Raise exception if tombstone to user-generated entity
            if tombstone is not None and tombstone.sources.user_generated_id is not None:
                raise StampedTombstoneError("Entity tombstones to user-generated entity: '%s' to '%s'" % \
                    (entity.entity_id, tombstone.entity_id))

        # Verify that at least one source exists
        if entity.sources is None or len(entity.sources.dataExport().keys()) == 0:
            raise StampedInvalidSourcesError("%s: Missing sources" % key)

        # Source-specific checks
        if entity.sources.itunes_id is not None and entity.sources.itunes_url is None:
            raise StampedItunesSourceError("%s: Missing iTunes URL" % entity.entity_id)
        if entity.sources.googleplaces_id is not None and entity.sources.googleplaces_reference is None:
            raise StampedGooglePlacesSourceError("%s: Missing Google Places reference" % entity.entity_id)

        # Menu check
        if entity.kind == 'place' and entity.menu == True:
            if self._collection._database['menus'].find({'_id': self._getObjectIdFromString(entity.entity_id)}).count() == 0:
                msg = "%s: Menu missing" % key
                if repair:
                    logs.info(msg)
                    del(entity.menu)
                    del(entity.menu_source)
                    del(entity.menu_timestamp)
                    modified = True
                else:
                    raise StampedDataError(msg)

        # Generate third_party_ids if it doesn't exist
        if (entity.third_party_ids is None or not entity.third_party_ids) and entity.sources.user_generated_id is None:
            msg = "%s: Missing third_party_ids" % key
            if repair:
                logs.info(msg)
                entity._maybeRegenerateThirdPartyIds()
                modified = True
            else:
                raise StampedDataError(msg)

        # Verify image exists
        if entity.images is not None:
            if entity.kind == 'place':
                msg = "%s: No image for places" % (key)
                if repair:
                    logs.info(msg)
                    del(entity.images)
                else:
                    raise StampedDataError(msg)
            else:
                images = []
                for image in entity.images:
                    sizes = []
                    for size in image.sizes:
                        if size.url.startswith('http://maps.gstatic.com'):
                            msg = "%s: Blacklisted image (%s)" % (key, size.url)
                            if repair:
                                logs.info(msg)
                                modified = True
                                continue
                            else:
                                raise StampedDataError(msg)
                        if getHeadRequest(size.url, maxDelay=4) is None:
                            msg = "%s: Image is unavailable (%s)" % (key, size.url)
                            if repair:
                                logs.info(msg)
                                modified = True
                                continue
                            else:
                                raise StampedDataError(msg)
                        if size.width is None or size.height is None:
                            msg = "%s: Image dimensions not defined (%s)" % (key, size.url)
                            if repair:
                                logs.info(msg)
                                try:
                                    size.width, size.height = getWebImageSize(size.url)
                                    modified = True
                                except Exception as e:
                                    logs.warning("%s: Could not get image sizes: %s" % (key, e))
                                    raise 
                            else:
                                raise StampedDataError(msg)
                        sizes.append(size)
                    if len(sizes) > 0:
                        image.sizes = sizes
                        images.append(image)
                if len(images) > 0:
                    entity.images = images
                else:
                    del(entity.images)

        if modified and repair:
            self._collection.update({'_id' : key}, self._convertToMongo(entity))
            print self._convertToMongo(entity)

        return True

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

