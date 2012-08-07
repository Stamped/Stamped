#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import pymongo, time
from logs       import report

try:
    import libs.ec2_utils

    from datetime                       import datetime, timedelta
    from utils                          import lazyProperty, getHeadRequest, getWebImageSize
    from bson.objectid                  import ObjectId

    from api_old.Schemas                        import *
    from api_old.Entity                         import getSimplifiedTitle, buildEntity

    from db.mongodb.AMongoCollection            import AMongoCollection
    from db.mongodb.MongoMenuCollection         import MongoMenuCollection
    from api_old.AEntityDB                              import AEntityDB
    from libs.Memcache                              import globalMemcache
    from difflib                                    import SequenceMatcher
    from api_old.ADecorationDB                          import ADecorationDB
    from errors                                     import StampedUnavailableError
    from logs                                       import log

    from libs.SearchUtils                           import generateSearchTokens
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
                'sources.netflix_id', 'sources.thetvdb_id', 'sources.nytimes_id', 'sources.umdmusic_id')

        self._collection.ensure_index([
                                    ('search_tokens',               pymongo.ASCENDING),
                                    ('sources.user_generated_id',   pymongo.ASCENDING),
                                    ('sources.tombstone_id',        pymongo.ASCENDING),
                                ])


        for field in fast_resolve_fields:
            self._collection.ensure_index(field)
        self._collection.ensure_index('search_tokens')
        self._collection.ensure_index('titlel')
        self._collection.ensure_index('albums.title')
        self._collection.ensure_index('artists.title')
        self._collection.ensure_index('authors.title')
        self._collection.ensure_index('tracks.title')

        self._collection.ensure_index([('_id', pymongo.ASCENDING), ('sources.user_generated_id', pymongo.ASCENDING)])

        self._cache = globalMemcache()

    @lazyProperty
    def seed_collection(self):
        return MongoEntitySeedCollection()

    @lazyProperty
    def entity_stats(self):
        return MongoEntityStatsCollection()

    @lazyProperty
    def whitelisted_tastemaker_entities(self):
        return MongoWhitelistedTastemakerEntityIdsCollection()

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

        document.pop('titlel', None)
        document.pop('search_tokens', None)

        entity = buildEntity(document, mini=mini)

        return entity

    def _convertToMongo(self, entity):
        if entity.entity_id is not None and entity.entity_id.startswith('T_'):
            del entity.entity_id

        # Extract search tokens
        searchTokens = generateSearchTokens(entity)

        # Convert document
        document = AMongoCollection._convertToMongo(self, entity)
        if document is None:
            return None

        # Add search tokens
        document['search_tokens'] = searchTokens

        # Add titlel
        if 'title' in document:
            document['titlel'] = getSimplifiedTitle(document['title'])

        return document


    ### CACHING

    def _getCachedEntity(self, entityId):
        key = str("obj::entity::%s" % entityId)
        return self._cache[key]

    def _setCachedEntity(self, entity):
        key = str("obj::entity::%s" % entity.entity_id)
        cacheLength = 60 * 10 # 10 minutes
        try:
            self._cache.set(key, entity, time=cacheLength)
        except Exception as e:
            logs.warning("Unable to set cache for %s: %s" % (entity.entity_id, e))

    def _delCachedEntity(self, entityId):
        key = str("obj::entity::%s" % entityId)
        try:
            del(self._cache[key])
        except KeyError:
            pass


    def _getCachedEntityMini(self, entityId):
        key = str("obj::entitymini::%s" % entityId)
        return self._cache[key]

    def _setCachedEntityMini(self, entity):
        key = str("obj::entitymini::%s" % entity.entity_id)
        cacheLength = 60 * 10 # 10 minutes
        try:
            self._cache.set(key, entity, time=cacheLength)
        except Exception as e:
            logs.warning("Unable to set cache for %s: %s" % (entity.entity_id, e))

    def _delCachedEntityMini(self, entityId):
        key = str("obj::entitymini::%s" % entityId)
        try:
            del(self._cache[key])
        except KeyError:
            pass


    ### INTEGRITY

    def checkIntegrity(self, key, repair=False, api=None):
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
        
        assert document is not None

        resolve = False
        modified = False

        # Check if old schema version
        if 'schema_version' not in document or 'search_tokens' not in document:
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
                    modified = True
                else:
                    raise StampedDataError(msg)

            # Check if tombstone is chained
            if tombstone is not None and tombstone.sources.tombstone_id is not None:
                if tombstone.sources.tombstone_id == entity.entity_id:
                    msg = "Entities tombstoned to each other: '%s' and '%s'" % (entity.entity_id, tombstone.entity_id)
                    raise StampedTombstoneError(msg)
                msg = "Entity tombstone chain: '%s' to '%s' to '%s'" % \
                    (entity.entity_id, tombstone.entity_id, tombstone.sources.tombstone_id)
                if repair:
                    logs.info(msg)
                    entity.sources.tombstone_id = tombstone.sources.tombstone_id
                    modified = True
                else:
                    raise StampedTombstoneError(msg)
                
            # Raise exception if tombstone to user-generated entity
            if tombstone is not None and tombstone.sources.user_generated_id is not None:
                raise StampedTombstoneError("Entity tombstones to user-generated entity: '%s' to '%s'" % \
                    (entity.entity_id, tombstone.entity_id))

        # Verify that at least one source exists
        if entity.sources is None or len(entity.sources.dataExport().keys()) == 0:
            raise StampedInvalidSourcesError("%s: Missing sources" % key)

        # iTunes: Verify 'url' exists
        if entity.sources.itunes_id is not None and entity.sources.itunes_url is None:
            msg = "%s: Missing iTunes URL" % key
            if repair:
                logs.info(msg)
                del(entity.sources.itunes_timestamp)
                resolve = True
                modified = True
            else:
                raise StampedDataError(msg)

        # iTunes: Verify 'url' points to 'http://itunes.apple.com'
        elif entity.sources.itunes_id is not None and entity.sources.itunes_url is not None:
            if not entity.sources.itunes_url.startswith('http://itunes.apple.com'):
                msg = "%s: Invalid iTunes URL" % key
                if repair:
                    logs.info(msg)
                    del(entity.sources.itunes_timestamp)
                    del(entity.sources.itunes_url)
                    resolve = True
                    modified = True
                else:
                    raise StampedDataError(msg)

        # Google: Verify 'reference' exists
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
                    del(entity.images_timestamp)
                    del(entity.images_source)
                    modified = True
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
                        # Sleep for half a second as a poor-man's rate limiter
                        # time.sleep(0.5)
                        # if getHeadRequest(size.url, maxDelay=4) is None:
                        #     msg = "%s: Image is unavailable (%s)" % (key, size.url)
                        #     if repair:
                        #         logs.info(msg)
                        #         modified = True
                        #         continue
                        #     else:
                        #         raise StampedDataError(msg)
                        # NOTE: This is hitting rate limits from Amazon, so commenting out for now
                        # if size.width is None or size.height is None:
                        #     msg = "%s: Image dimensions not defined (%s)" % (key, size.url)
                        #     if repair:
                        #         logs.info(msg)
                        #         try:
                        #             size.width, size.height = getWebImageSize(size.url)
                        #             modified = True
                        #         except Exception as e:
                        #             logs.warning("%s: Could not get image sizes: %s" % (key, e))
                        #             raise 
                        #     else:
                        #         raise StampedDataError(msg)
                        sizes.append(size)
                    if len(sizes) > 0:
                        image.sizes = sizes
                        images.append(image)
                if len(images) > 0:
                    entity.images = images
                else:
                    del(entity.images)

            if entity.images_source == 'seed':
                msg = "%s: Image source set as seed" % key
                if repair:
                    logs.info(msg)
                    del(entity.images_source)
                    modified = True
                else:
                    raise StampedDataError(msg)

        # Check that any existing links are valid
        def _checkLink(field):
            if hasattr(entity, field) and getattr(entity, field) is not None:
                valid = []
                for item in getattr(entity, field):
                    if hasattr(item, 'entity_id') and item.entity_id is not None:
                        if self._collection.find({'_id': self._getObjectIdFromString(item.entity_id)}).count() == 0:
                            msg = "%s: Invalid link within %s (%s)" % (key, field, item.entity_id)
                            if repair:
                                logs.info(msg)
                                del(item.entity_id)
                                modified = True
                            else:
                                raise StampedDataError(msg)
                    valid.append(item)
                setattr(entity, field, valid)

        linkedFields = ['artists', 'albums', 'tracks', 'directors', 'movies', 'books', 'authors', 'cast']
        for field in linkedFields:
            _checkLink(field)

        if modified and repair:
            self._collection.update({'_id' : key}, self._convertToMongo(entity))

        if resolve and repair:
            msg = "%s: Re-resolve entity" % key
            # Only run this on EC2 (for now)
            if api is not None:
                if libs.ec2_utils.is_ec2():
                    logs.info(msg)
                    api.mergeEntityId(str(key))
            else:
                raise StampedDataError(msg)

        # Check integrity for stats
        if entity.sources.tombstone_id is None:
            self.entity_stats.checkIntegrity(key, repair=repair, api=api)

        return True

    ### PUBLIC

    def addEntity(self, entity):
        if entity.timestamp is None:
            entity.timestamp = BasicTimestamp()
        entity.timestamp.created = datetime.utcnow()
        
        entity = self._addObject(entity)
        self.seed_collection.addEntity(entity)
        self._setCachedEntity(entity)
        return entity

    def getEntityMini(self, entityId):
        try:
            return self._getCachedEntityMini(entityId)
        except KeyError:
            pass 

        documentId  = self._getObjectIdFromString(entityId)
        params = {'_id' : documentId}
        fields = {'details.artist' : 0, 'tracks' : 0, 'albums' : 0, 'cast' : 0, 'desc' : 0  }

        documents = self._collection.find(params, fields)
        if documents.count() == 0:
            raise StampedDocumentNotFoundError("Unable to find entity (id = %s)" % documentId)
        entity = self._convertFromMongo(documents[0])
        entity = entity.minimize()

        self._setCachedEntityMini(entity)

        return entity

    def getEntity(self, entityId, forcePrimary=False):
        if not forcePrimary:
            try:
                return self._getCachedEntity(entityId)
            except KeyError:
                pass 

        documentId  = self._getObjectIdFromString(entityId)
        document    = self._getMongoDocumentFromId(documentId, forcePrimary=forcePrimary)
        entity      = self._convertFromMongo(document)

        self._setCachedEntity(entity)

        return entity

    def getEntityMinis(self, entityIds):
        result = []

        documentIds = []
        for entityId in entityIds:
            try:
                result.append(self._getCachedEntityMini(entityId))
            except KeyError:
                documentIds.append(self._getObjectIdFromString(entityId))
        params = {'_id': {'$in': documentIds}}
        fields = {'details.artist' : 0, 'tracks' : 0, 'albums' : 0, 'cast' : 0, 'desc' : 0  }

        documents = self._collection.find(params, fields)

        for document in documents:
            entity = self._convertFromMongo(document, mini=False)
            entity = entity.minimize()
            self._setCachedEntityMini(entity)
            result.append(entity)

        return result

    def getEntities(self, entityIds):
        result = []

        documentIds = []
        for entityId in entityIds:
            try:
                result.append(self._getCachedEntity(entityId))
            except KeyError:
                documentIds.append(self._getObjectIdFromString(entityId))
        documents = self._getMongoDocumentsFromIds(documentIds)

        for document in documents:
            entity = self._convertFromMongo(document)
            self._setCachedEntity(entity)
            result.append(entity)

        return result

    def getEntitiesByQuery(self, queryDict):
        return (self._convertFromMongo(item) for item in self._collection.find(queryDict))

    def updateEntity(self, entity):
        document = self._convertToMongo(entity)
        document = self._updateMongoDocument(document)
        entity = self._convertFromMongo(document)
        self._setCachedEntity(entity)
        return entity

    def removeEntity(self, entityId):
        self._delCachedEntity(entityId)
        documentId = self._getObjectIdFromString(entityId)
        return self._removeMongoDocument(documentId)

    def removeCustomEntity(self, entityId, userId):
        try:
            query = {'_id': self._getObjectIdFromString(entityId), 'sources.user_generated_id': userId}
            self._collection.remove(query)
            self._delCachedEntity(entityId)
            return True
        except Exception:
            logs.warning("Cannot remove custom entity")
            raise

    def addEntities(self, entities):
        entities = self._addObjects(entities)
        for entity in entities:
            self._setCachedEntity(entity)
        return entities

    def updateDecoration(self, name, value):
        if name == 'menu':
            self.__menu_db.updateMenu(value)

    def getWhitelistedTastemakerEntityIds(self, section):
        return self.whitelisted_tastemaker_entities.getEntityIds(section)



class MongoEntityStatsCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='entitystats', primary_key='entity_id', obj=EntityStats)
        
        self._collection.ensure_index([ 
            ('types', pymongo.ASCENDING),
            ('score', pymongo.DESCENDING),
        ])
        self._collection.ensure_index([ 
            ('types', pymongo.ASCENDING),
            ('lat', pymongo.ASCENDING), 
            ('lng', pymongo.ASCENDING), 
            ('score', pymongo.DESCENDING),
        ])

        self._cache = globalMemcache()

    ### INTEGRITY

    def checkIntegrity(self, key, repair=False, api=None):
        """
        Check an entity's stats to verify the following things:

        - Entity still exists 

        - Stats are not out of date 

        - Length of popular stamps equals length of popular users

        """

        regenerate = False
        document = None

        # Remove stat if entity no longer exists
        if self._collection._database['entities'].find({'_id': key}).count() == 0:
            msg = "%s: Entity no longer exists"
            if repair:
                logs.info(msg)
                self._removeMongoDocument(key)
                return True
            else:
                raise StampedDataError(msg)
        
        # Verify stat exists
        try:
            document = self._getMongoDocumentFromId(key)
        except StampedDocumentNotFoundError:
            msg = "%s: Stat not found" % key
            if repair:
                logs.info(msg)
                regenerate = True
            else:
                raise StampedDataError(msg)

        # Check if old schema version
        if document is not None and 'timestamp' not in document:
            msg = "%s: Old schema" % key
            if repair:
                logs.info(msg)
                regenerate = True
            else:
                raise StampedDataError(msg)

        # Check if stats are stale
        elif document is not None and 'timestamp' in document:
            generated = document['timestamp']['generated']
            if generated < datetime.utcnow() - timedelta(days=2):
                msg = "%s: Stale stats" % key
                if repair:
                    logs.info(msg)
                    regenerate = True 
                else:
                    raise StampedDataError(msg)

        if document is not None and 'popular_users' in document and 'popular_stamps' in document:
            if len(document['popular_users']) != len(document['popular_stamps']):
                msg = "%s: Popular users != Popular stamps" % key 
                if repair:
                    logs.info(msg)
                    regenerate = True 
                else:
                    raise StampedDataError(msg)

        # Rebuild
        if regenerate and repair:
            if api is not None:
                api.updateEntityStatsAsync(str(key))
            else:
                raise Exception("%s: API required to regenerate stats" % key)

        return True


    ### CACHING

    def _getCachedStat(self, entityId):
        key = str("obj::entitystat::%s" % entityId)
        return self._cache[key]

    def _setCachedStat(self, stat):
        key = str("obj::entitystat::%s" % stat.entity_id)
        cacheLength = 60 * 60 # 1 hour
        try:
            self._cache.set(key, stat, time=cacheLength)
        except Exception as e:
            logs.warning("Unable to set cache for %s: %s" % (stat.entity_id, e))

    def _delCachedStat(self, entityId):
        key = str("obj::entitystat::%s" % entityId)
        try:
            del(self._cache[key])
        except KeyError:
            pass

    
    ### PUBLIC
    
    def addEntityStats(self, stats):
        if stats.timestamp is None:
            stats.timestamp = StatTimestamp()
        stats.timestamp.generated = datetime.utcnow()

        result = self._addObject(stats)

        self._setCachedStat(result)

        return result
    
    def getEntityStats(self, entityId):
        try:
            return self._getCachedStat(entityId)
        except KeyError:
            pass

        documentId = self._getObjectIdFromString(entityId)
        document = self._getMongoDocumentFromId(documentId)
        result = self._convertFromMongo(document)
        self._setCachedStat(result)

        return result
        
    def getStatsForEntities(self, entityIds):
        result = []

        documentIds = []
        for entityId in entityIds:
            try:
                result.append(self._getCachedStat(entityId))
            except KeyError:
                documentIds.append(self._getObjectIdFromString(entityId))
        documents = self._getMongoDocumentsFromIds(documentIds)

        for document in documents:
            stat = self._convertFromMongo(document)
            self._setCachedStat(stat)
            result.append(stat)

        return result
    
    def saveEntityStats(self, stats):
        if stats.timestamp is None:
            stats.timestamp = StatTimestamp()
        stats.timestamp.generated = datetime.utcnow()

        result = self.update(stats)

        self._setCachedStat(result)

        return result
    
    def removeEntityStats(self, entityId):
        documentId = self._getObjectIdFromString(entityId)
        result = self._removeMongoDocument(documentId)
        self._delCachedStat(entityId)

        return result
    
    def _buildPopularQuery(self, **kwargs):
        types = kwargs.pop('types', None)
        viewport = kwargs.pop('viewport', None)

        query = {}

        if types is not None:
            query['types'] = {'$in': list(types)}

        if viewport is not None:
            query["lat"] = {
                "$gte" : viewport.lower_right.lat, 
                "$lte" : viewport.upper_left.lat, 
            }
            
            if viewport.upper_left.lng <= viewport.lower_right.lng:
                query["lng"] = { 
                    "$gte" : viewport.upper_left.lng, 
                    "$lte" : viewport.lower_right.lng, 
                }
            else:
                # handle special case where the viewport crosses the +180 / -180 mark
                query["$or"] = [{
                        "lng" : {
                            "$gte" : viewport.upper_left.lng, 
                        }, 
                    }, 
                    {
                        "lng" : {
                            "$lte" : viewport.lower_right.lng, 
                        }, 
                    }, 
                ]

        return query
    
    def getPopularEntityStats(self, **kwargs):
        limit = kwargs.pop('limit', 1000)

        query = self._buildPopularQuery(**kwargs)

        documents = self._collection.find(query) \
                        .sort([('score', pymongo.DESCENDING)]) \
                        .limit(limit)

        try:
            return map(self._convertFromMongo, documents)
        except Exception:
            logs.warning("Failed for query %s" % query)
            raise

class MongoEntitySeedCollection(AMongoCollection, AEntityDB):
    
    def __init__(self, collection='entities'):
        AMongoCollection.__init__(self, collection='seedentities', primary_key='entity_id', overflow=True)
        AEntityDB.__init__(self)
    
    def _convertFromMongo(self, document):
        if document is None:
            return None

        if '_id' in document and self._primary_key is not None:
            document[self._primary_key] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])

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
        return self._addObject(entity)

# For use with tastemaker guide
class MongoWhitelistedTastemakerEntityIdsCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='tastemaker_guide_whitelist', overflow=True)

    ### PUBLIC
    
    def getEntityIds(self, section):
        documents = self._getRelationships(section)
        return documents


