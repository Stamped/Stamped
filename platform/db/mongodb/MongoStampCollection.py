#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import bson, logs, pprint, pymongo, re

from datetime                           import datetime, timedelta
from utils                              import lazyProperty
from api_old.Schemas                        import *
from api_old.Entity                             import buildEntity, getSimplifiedTitle
from pprint                             import pprint

from api_old.AStampDB                       import AStampDB
from db.mongodb.AMongoCollection                   import AMongoCollection
from db.mongodb.AMongoCollectionView               import AMongoCollectionView
from db.mongodb.MongoUserLikesCollection           import MongoUserLikesCollection
from db.mongodb.MongoUserLikesHistoryCollection    import MongoUserLikesHistoryCollection
from db.mongodb.MongoStampLikesCollection          import MongoStampLikesCollection
from db.mongodb.MongoUserStampsCollection          import MongoUserStampsCollection
from db.mongodb.MongoInboxStampsCollection         import MongoInboxStampsCollection
from db.mongodb.MongoCreditGiversCollection        import MongoCreditGiversCollection
from db.mongodb.MongoCreditReceivedCollection      import MongoCreditReceivedCollection

from libs.Memcache                                      import globalMemcache, generateKeyFromDictionary

class MongoStampCollection(AMongoCollectionView, AStampDB):
    
    def __init__(self):
        AMongoCollectionView.__init__(self, collection='stamps', primary_key='stamp_id', obj=Stamp, overflow=True)
        AStampDB.__init__(self)
        
        self._collection.ensure_index([('timestamp.modified', pymongo.ASCENDING)])
        self._collection.ensure_index([('timestamp.created', pymongo.DESCENDING)])
        self._collection.ensure_index([('timestamp.stamped', pymongo.ASCENDING)])
        self._collection.ensure_index([('user.user_id', pymongo.ASCENDING), ('entity.entity_id', pymongo.ASCENDING)])
        self._collection.ensure_index([('user.user_id', pymongo.ASCENDING), ('stats.stamp_num', pymongo.ASCENDING)])
        self._collection.ensure_index([('entity.entity_id', pymongo.ASCENDING), ('credits.user.user_id', pymongo.ASCENDING)])
        self._collection.ensure_index([('credits.user.user_id', pymongo.ASCENDING)])
        
        # Indices for _getTimeSlice within AMongoCollectionView
        self._collection.ensure_index([('_id', pymongo.ASCENDING), ('entity.types', pymongo.ASCENDING), ('timestamp.stamped', pymongo.DESCENDING)])
        self._collection.ensure_index([('_id', pymongo.ASCENDING), ('timestamp.stamped', pymongo.DESCENDING)])
        self._collection.ensure_index([('entity.types', pymongo.ASCENDING), ('timestamp.stamped', pymongo.DESCENDING)])

        # Indices for _getSearchSlice
        self._collection.ensure_index([ ('_id', pymongo.ASCENDING), 
                                        ('entity.types', pymongo.ASCENDING), 
                                        ('search_blurb', pymongo.ASCENDING), 
                                        ('entity.coordinates.lng', pymongo.ASCENDING), 
                                        ('entity.coordinates.lat', pymongo.ASCENDING), 
                                        ('timestamp.stamped', pymongo.DESCENDING) ])
        
        self._collection.ensure_index([ ('_id', pymongo.ASCENDING), 
                                        ('entity.types', pymongo.ASCENDING), 
                                        ('entity.coordinates.lng', pymongo.ASCENDING), 
                                        ('entity.coordinates.lat', pymongo.ASCENDING), 
                                        ('timestamp.stamped', pymongo.DESCENDING) ])

        self._collection.ensure_index([ ('entity.types', pymongo.ASCENDING), 
                                        ('entity.coordinates.lng', pymongo.ASCENDING), 
                                        ('entity.coordinates.lat', pymongo.ASCENDING), 
                                        ('timestamp.stamped', pymongo.DESCENDING) ])


    def _upgradeDocument(self, document):
        if document is None:
            return None

        # Convert single-blurb documents into new multi-blurb schema
        if 'contents' not in document:
            if 'created' in document['timestamp']:
                created = document['timestamp']['created']
            else:
                try:
                    created = ObjectId(document['_id']).generation_time.replace(tzinfo=None)
                except Exception as e:
                    logs.warning("Unable to convert ObjectId to timestamp: %s" % e)
                    created = datetime.utcnow()
            contents =  {
                'blurb'     : document.pop('blurb', None),
                'timestamp' : { 'created' : created },
            }
            if 'image_dimensions' in document:
                contents['images'] = [
                    {
                        'sizes' :
                        [
                            {
                                'width'     : document['image_dimensions'].split(',')[0],
                                'height'    : document['image_dimensions'].split(',')[1],
                                'url'       : 'http://static.stamped.com/stamps/%s.jpg' % document['_id'],
                            }
                        ]
                    }
                ]
            document['contents'] = [ contents ]
            document['timestamp']['stamped'] = created

        else:
            # Temp: clean bad dev data (should never exist on prod)
            contents = []
            for content in document['contents']:
                if 'mentions' in content:
                    del(content['mentions'])
                contents.append(content)
            document['contents'] = contents

        if 'credit' in document:
            document['credits'] = document['credit']
            del(document['credit'])

        if 'credits' in document:
            credit = []
            for item in document['credits']:
                if 'user' in item:
                    credit.append(item)
                elif 'user_id' in item:
                    creditItem = {}
                    creditItem['user'] = {'user_id' : item['user_id']}
                    if 'stamp_id' in item:
                        creditItem['stamp_id'] = item['stamp_id']
                    credit.append(creditItem)
            document['credits'] = credit

        return document

    def _convertToMongo(self, stamp):
        document = AMongoCollectionView._convertToMongo(self, stamp)

        searchBlurb = getSimplifiedTitle(stamp.entity.title)
        for content in stamp.contents:
            if content.blurb is not None:
                searchBlurb = "%s %s" % (searchBlurb, getSimplifiedTitle(content.blurb))
        
        document['search_blurb'] = searchBlurb
        return document
    
    def _convertFromMongo(self, document):
        if document is None:
            return None

        if 'search_blurb' in document:
            del(document['search_blurb'])

        document = self._upgradeDocument(document)
        
        if '_id' in document and self._primary_key is not None:
            document[self._primary_key] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])

        entityData = document.pop('entity')
        document['entity'] = {'entity_id': entityData['entity_id']}
        
        stamp = self._obj().dataImport(document, overflow=self._overflow)

        try:
            entity = buildEntity(entityData, mini=True)
            stamp.entity = entity
        except Exception as e:
            logs.warning("Unable to upgrade entity embedded within stamp '%s'" % (stamp.stamp_id))

        return stamp 


    ### INTEGRITY

    def checkIntegrity(self, key, repair=False, api=None):
        document = self._getMongoDocumentFromId(key)
        
        assert document is not None

        modified = False

        # Check if old schema version
        if 'contents' not in document or 'credit' in document or 'search_blurb' not in document:
            msg = "%s: Old schema" % key
            if repair:
                logs.info(msg)
                modified = True
            else:
                raise StampedDataError(msg)

        stamp = self._convertFromMongo(document)

        # Verify that user exists
        userId = stamp.user.user_id
        if self._collection._database['users'].find({'_id': self._getObjectIdFromString(userId)}).count() == 0:
            msg = "%s: User not found (%s)" % (key, userId)
            raise StampedDataError(msg)

        # Verify that any credited users exist
        if stamp.credits is not None:
            credits = []
            for credit in stamp.credits:
                creditedUserId = credit.user.user_id
                query = {'_id' : self._getObjectIdFromString(creditedUserId)}
                if self._collection._database['users'].find(query).count() == 1:
                    credits.append(credit)
                else:
                    msg = "%s: Credited user not found (%s)" % (key, creditedUserId)
                    if repair:
                        logs.info(msg)
                        modified = True
                    else:
                        raise StampedDataError(msg)
            if len(credits) > 0:
                stamp.credits = credits
            else:
                msg = "%s: Cleaning up credits" % key
                logs.info(msg)
                if repair:
                    del(stamp.credits)
                    modified = True

        # Verify that entity exists
        entityId = stamp.entity.entity_id
        entityDocument = self._collection._database['entities'].find_one({'_id' : self._getObjectIdFromString(entityId)})
        if entityDocument is None:
            msg = "%s: Entity not found (%s)" % (key, entityId)
            raise StampedDataError(msg)
        entity = buildEntity(entityDocument)

        # Check if entity has been tombstoned and update entity if so
        if entity.sources.tombstone_id is not None:
            msg = "%s: Entity tombstoned to new entity" % (key)
            if repair:
                logs.info(msg)
                tombstoneId = entity.sources.tombstone_id
                tombstone = self._collection._database['entities'].find_one({'_id' : self._getObjectIdFromString(tombstoneId)})
                if tombstone is None:
                    msg = "%s: New tombstone entity not found (%s)" % (key, tombstoneId)
                    raise StampedDataError(msg)
                stamp.entity = buildEntity(tombstone).minimize()
                modified = True
            else:
                raise StampedDataError(msg)

        # Check if entity stub has been updated
        else:
            if stamp.entity != entity.minimize():
                msg = "%s: Embedded entity is stale" % key
                if repair:
                    logs.info(msg)
                    stamp.entity = entity.minimize()
                    modified = True
                else:
                    raise StampedDataError(msg)

        # Verify that stamp number is unique
        stampNum = stamp.stats.stamp_num
        duplicateStamps = self._collection.find({'user.user_id' : userId, 'stats.stamp_num' : stampNum})
        if duplicateStamps.count() > 1:
            msg = "%s: Multiple stamps exist for userId '%s' and stampNum '%s'" % (key, userId, stampNum)
            raise StampedDataError(msg)

        # Verify that this is the only stamp for this user for this entity
        if self._collection.find({'user.user_id': userId, 'entity.entity_id': stamp.entity.entity_id}).count() > 1:
            msg = "%s: Multiple stamps exist for user '%s' and entity '%s'" % (key, userId, stamp.entity.entity_id)
            raise StampedDataError(msg)

        ### TODO
        # Check if temp_image_url exists -> kick off async process
        # Check that image[s] have dimensions
        # Verify image url exists?
        # Check if stats need to be updated?

        if modified and repair:
            self._collection.update({'_id' : key}, self._convertToMongo(stamp))

        # Check integrity for stats
        self.stamp_stats.checkIntegrity(key, repair=repair, api=api)

        return True
    
    ### PUBLIC
    
    @lazyProperty
    def user_stamps_collection(self):
        return MongoUserStampsCollection()
    
    @lazyProperty
    def inbox_stamps_collection(self):
        return MongoInboxStampsCollection()
    
    @lazyProperty
    def credit_givers_collection(self):
        return MongoCreditGiversCollection()
    
    @lazyProperty
    def credit_received_collection(self):
        return MongoCreditReceivedCollection()
    
    @lazyProperty
    def stamp_likes_collection(self):
        return MongoStampLikesCollection()
    
    @lazyProperty
    def user_likes_collection(self):
        return MongoUserLikesCollection()
    
    @lazyProperty
    def user_likes_history_collection(self):
        return MongoUserLikesHistoryCollection()

    @lazyProperty
    def stamp_stats(self):
        return MongoStampStatsCollection()

    @lazyProperty
    def whitelisted_tastemaker_stamps(self):
        return MongoWhitelistedTastemakerStampIdsCollection()
    
    def addStamp(self, stamp):
        return self._addObject(stamp)
    
    def getStamp(self, stampId):
        documentId = self._getObjectIdFromString(stampId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)
    
    def updateStamp(self, stamp):
        return self.update(stamp)
    
    def removeStamp(self, stampId):
        documentId = self._getObjectIdFromString(stampId)
        result = self._removeMongoDocument(documentId)

        return result
    
    def addUserStampReference(self, userId, stampId):
        # Add a reference to the stamp in the user's collection
        self.user_stamps_collection.addUserStamp(userId, stampId)
    
    def removeUserStampReference(self, userId, stampId):
        # Remove a reference to the stamp in the user's collection
        self.user_stamps_collection.removeUserStamp(userId, stampId)
    
    def removeAllUserStampReferences(self, userId):
        self.user_stamps_collection.removeAllUserStamps(userId)
    
    def addInboxStampReference(self, userIds, stampId):
        if not isinstance(userIds, list):
            userIds = [ userIds ]
        # Add a reference to the stamp in followers' inbox
        self.inbox_stamps_collection.addInboxStamps(userIds, stampId)
    
    def removeInboxStampReference(self, userIds, stampId):
        # Remove a reference to the stamp in followers' inbox
        self.inbox_stamps_collection.removeInboxStamps(userIds, stampId)
    
    def addInboxStampReferencesForUser(self, userId, stampIds):
        self.inbox_stamps_collection.addInboxStampsForUser(userId, stampIds)
    
    def removeInboxStampReferencesForUser(self, userId, stampIds):
        self.inbox_stamps_collection.removeInboxStampsForUser(userId, stampIds)
    
    def removeAllInboxStampReferences(self, userId):
        self.inbox_stamps_collection.removeAllInboxStamps(userId)
    
    def getStamps(self, stampIds, **kwargs):
        sort = kwargs.pop('sort', None)
        if sort in ['modified', 'created', 'stamped']:
            sort = 'timestamp.%s' % sort
        else:
            sort = 'timestamp.stamped'
        
        params = {
            'since':    kwargs.pop('since', None),
            'before':   kwargs.pop('before', None), 
            'limit':    kwargs.pop('limit', 0),
            'sort':     sort,
            'sortOrder': pymongo.DESCENDING, 
        }
        
        ids = map(self._getObjectIdFromString, stampIds)
        
        # Get stamps
        documents = self._getMongoDocumentsFromIds(ids, **params)
        
        return map(self._convertFromMongo, documents)
    
    def getStampCollectionSlice(self, stampIds, timeSlice):
        if stampIds is not None:
            if len(stampIds) == 0:
                return []
            
            ids = map(self._getObjectIdFromString, stampIds)
            
            if len(ids) == 1:
                query   = { '_id' : ids[0] }
            else:
                query   = { '_id' : { '$in' : ids } }
        else:
            query   = { }
        
        return self._getTimeSlice(query, timeSlice)
    
    def searchStampCollectionSlice(self, stampIds, searchSlice):
        if stampIds is not None:
            if len(stampIds) == 0:
                return []
            
            ids = map(self._getObjectIdFromString, stampIds)
            
            if len(ids) == 1:
                query   = { '_id' : ids[0] }
            else:
                query   = { '_id' : { '$in' : ids } }
        else:
            query   = { }
        
        return self._getSearchSlice(query, searchSlice)
    
    def countStamps(self, userId):
        return len(self.user_stamps_collection.getUserStampIds(userId))
    
    def countStampsForEntity(self, entityId, userIds=None):
        query = { 'entity.entity_id' : entityId }

        if userIds is not None:
            if len(userIds) == 0:
                return []
            
            if len(userIds) == 1:
                query['user.user_id'] = userIds[0]
            else:
                query['user.user_id'] = { '$in' : userIds }

        return self._collection.find(query).count()
    
    def updateStampStats(self, stampId, stat, value=None, increment=1):
        key = 'stats.%s' % (stat)
        if value is not None:
            self._collection.update(
                {'_id': self._getObjectIdFromString(stampId)}, 
                {'$set': {key: value, 'timestamp.modified': datetime.utcnow()}},
                upsert=True)
        else:
            self._collection.update(
                {'_id': self._getObjectIdFromString(stampId)}, 
                {'$inc': {key: increment}, 
                 '$set': {'timestamp.modified': datetime.utcnow()}},
                upsert=True)

    def updateStampOGActionId(self, stampId, og_action_id):
        self._collection.update({'_id': self._getObjectIdFromString(stampId)}, {'$set': {'og_action_id': og_action_id}})

    def updateStampEntity(self, stampId, entity):
        self._collection.update({'_id': self._getObjectIdFromString(stampId)}, {'$set': {'entity': entity.dataExport()}})

    def getStampFromUserEntity(self, userId, entityId):
        try:
            document = self._collection.find_one({
                'user.user_id': userId, 
                'entity.entity_id': entityId,
            })
            return self._convertFromMongo(document)
        except Exception:
            return None

    def checkStamp(self, userId, entityId):
        return self.getStampFromUserEntity(userId, entityId) is not None
    
    def getStampsFromUsersForEntity(self, userIds, entityId):
        try:
            documents = self._collection.find({
                'user.user_id' : { '$in' : userIds }, 
                'entity.entity_id' : entityId,
            })
            return map(self._convertFromMongo, documents)
        except Exception:
            return []

    def getStampsForEntity(self, entityId, limit=None):
        try:
            docs = self._collection.find({'entity.entity_id': entityId})
            if limit is not None:
                docs = docs.limit(limit)
            return list(self._convertFromMongo(doc) for doc in docs)
        except Exception as e:
            logs.warning("Could not get stamps for entity '%s': %s" % (entityId, e))
            return []

    def getStampIdsForEntity(self, entityId, limit=None):
        try:
            docs = self._collection.find({'entity.entity_id': entityId}, fields=['_id'])
            if limit is not None:
                docs = docs.limit(limit)
            return list(self._getStringFromObjectId(doc['_id']) for doc in docs)
        except Exception as e:
            logs.warning("Could not get stamp ids for entity '%s': %s" % (entityId, e))
            return []
    
    def getStampFromUserStampNum(self, userId, stampNum):
        try:
            stampNum = int(stampNum)
            document = self._collection.find_one({
                'user.user_id': userId, 
                'stats.stamp_num': stampNum,
            })
            if document is None:
                raise StampedDocumentNotFoundError("Unable to find document for user %s and stamp num %s" % (userId, stampNum))
            return self._convertFromMongo(document)
        except Exception:
            return None
    
    def giveCredit(self, creditedUserId, stampId, userId):
        # Add to 'credit received'
        ### TODO: Does this belong here?
        self.credit_received_collection.addCredit(creditedUserId, stampId)
        
        # Add to 'credit givers'
        ### TODO: Does this belong here?
        self.credit_givers_collection.addGiver(creditedUserId, userId)
    
    def removeCredit(self, creditedUserId, stampId, userId):
        # Add to 'credit received'
        ### TODO: Does this belong here?
        self.credit_received_collection.removeCredit(creditedUserId, stampId)
        
        # Add to 'credit givers'
        ### TODO: Does this belong here?
        self.credit_givers_collection.removeGiver(creditedUserId, userId)

    def checkCredit(self, creditedUserId, stamp):
        credits = self.credit_received_collection.getCredit(creditedUserId)
        if stamp.stamp_id in credits:
            return True
        return False 
    
    def countCredits(self, userId):
        return self.credit_received_collection.numCredit(userId)

    def getCreditedStamps(self, userId, entityId, limit=0):
        try:
            ### TODO: User credit_received_collection?
            query = {
                'entity.entity_id'      : entityId,
                'credits.user.user_id'  : userId,
            }
            documents = self._collection.find(query).limit(limit)
            return map(self._convertFromMongo, documents)
        except Exception:
            return []
        
    def addLike(self, userId, stampId):
        # Add a reference to the user in the stamp's 'like' collection
        self.stamp_likes_collection.addStampLike(stampId, userId) 
        # Add a reference to the stamp in the user's 'like' collection
        self.user_likes_collection.addUserLike(userId, stampId) 
        # Add a reference to the stamp in the user's 'like' history collection
        self.user_likes_history_collection.addUserLike(userId, stampId)
        # Update the modified timestamp
        self._collection.update({'_id': self._getObjectIdFromString(stampId)}, 
            {'$set': {'timestamp.modified': datetime.utcnow()}})
    
    def removeLike(self, userId, stampId):
        # Remove a reference to the user in the stamp's 'like' collection
        stampLike = self.stamp_likes_collection.removeStampLike(stampId, userId)
        # Remove a reference to the stamp in the user's 'like' collection
        userLike = self.user_likes_collection.removeUserLike(userId, stampId) 
        
        if stampLike == True and userLike == True:
            return True
        return False
        
    def getStampLikes(self, stampId):
        # Returns user ids that have "liked" the stamp
        return self.stamp_likes_collection.getStampLikes(stampId)
        
    def getUserLikes(self, userId):
        # Return stamp ids that a user has "liked"
        return self.user_likes_collection.getUserLikes(userId) 

    def getUserLikesHistory(self, userId):
        return self.user_likes_history_collection.getUserLikes(userId)

    def removeUserLikesHistory(self, userId):
        return self.user_likes_history_collection.removeUserLikes(userId)
    
    def countStampLikes(self, stampId):
        return len(self.getStampLikes(stampId))
    
    def countUserLikes(self, userId):
        return len(self.getUserLikes(userId))
    
    def checkLike(self, userId, stampId):
        try:
            likes = self.stamp_likes_collection.getStampLikes(stampId) 
            if userId in likes:
                return True
            raise
        except Exception:
            return False
    
    def removeStamps(self, stampIds):
        if stampIds is None or len(stampIds) == 0:
            raise Exception("Must pass stampIds to delete!")
        documentIds = []
        for stampId in stampIds:
            documentIds.append(self._getObjectIdFromString(stampId))
        result = self._removeMongoDocuments(documentIds)
        
        return result

    def getWhitelistedTastemakerStampIds(self):
        return self.whitelisted_tastemaker_stamps.getStampIds()


class MongoStampStatsCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='stampstats', primary_key='stamp_id', obj=StampStats)
        self._collection.ensure_index([ ('entity_id', pymongo.ASCENDING), ('last_stamped', pymongo.ASCENDING), ('score', pymongo.DESCENDING) ])
        self._collection.ensure_index([ ('last_stamped', pymongo.ASCENDING), ('score', pymongo.DESCENDING) ])
        self._collection.ensure_index([ ('entity_id', pymongo.ASCENDING), ('score', pymongo.DESCENDING) ])
        self._cache = globalMemcache()

    ### INTEGRITY

    def checkIntegrity(self, key, repair=False, api=None):
        """
        Check a stamp's stats to verify the following things:

        - Stamp still exists 

        - Stats are not out of date 

        """

        regenerate = False
        document = None

        # Remove stat if stamp no longer exists
        if self._collection._database['stamps'].find({'_id': key}).count() == 0:
            msg = "%s: Stamp no longer exists"
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

        # Rebuild
        if regenerate and repair:
            if api is not None:
                api.updateStampStatsAsync(str(key))
            else:
                raise Exception("%s: API required to regenerate stats" % key)

        return True


    ### CACHING

    def _getCachedStat(self, stampId):
        key = str("obj::stampstat::%s" % stampId)
        return self._cache[key]

    def _setCachedStat(self, stat):
        key = str("obj::stampstat::%s" % stat.stamp_id)
        cacheLength = 60 * 60 # 1 hour
        try:
            self._cache.set(key, stat, time=cacheLength)
        except Exception as e:
            logs.warning("Unable to set cache for %s: %s" % (stat.stamp_id, e))

    def _delCachedStat(self, stampId):
        key = str("obj::stampstat::%s" % stampId)
        try:
            del(self._cache[key])
        except KeyError:
            pass


    ### PUBLIC
    
    def addStampStats(self, stats):
        if stats.timestamp is None:
            stats.timestamp = StatTimestamp()
        stats.timestamp.generated = datetime.utcnow()

        result = self._addObject(stats)

        self._setCachedStat(result)

        return result
    
    def getStampStats(self, stampId):
        try:
            return self._getCachedStat(stampId)
        except KeyError:
            pass

        documentId = self._getObjectIdFromString(stampId)
        document = self._getMongoDocumentFromId(documentId)
        result = self._convertFromMongo(document)
        self._setCachedStat(result)

        return result

    def getStatsForStamps(self, stampIds):
        result = []

        documentIds = []
        for stampId in stampIds:
            try:
                result.append(self._getCachedStat(stampId))
            except KeyError:
                documentIds.append(self._getObjectIdFromString(stampId))
        documents = self._getMongoDocumentsFromIds(documentIds)

        for document in documents:
            stat = self._convertFromMongo(document)
            self._setCachedStat(stat)
            result.append(stat)

        return result
    
    def updateStampStats(self, stats):
        if stats.timestamp is None:
            stats.timestamp = StatTimestamp()
        stats.timestamp.generated = datetime.utcnow()

        result = self.update(stats)

        self._setCachedStat(result)

        return result
    
    def removeStampStats(self, stampId):
        documentId = self._getObjectIdFromString(stampId)
        result = self._removeMongoDocument(stampId)
        self._delCachedStat(stampId)

        return result
    
    def removeStatsForStamps(self, stampIds):
        documentIds = map(self._getObjectIdFromString, stampIds)
        result = self._removeMongoDocuments(documentIds)
        
        for stampId in stampIds:
            self._delCachedStat(stampId)

        return result

    def _buildPopularQuery(self, **kwargs):
        since       = kwargs.pop('since', None)
        before      = kwargs.pop('before', None)
        entityId    = kwargs.pop('entityId', None)
        minScore    = kwargs.pop('minScore', None)

        query = {}

        if entityId is not None:
            query['entity_id'] = entityId

        if since is not None and before is not None:
            query['last_stamped'] = {'$gte': since, '$lte': before}
        elif since is not None:
            query['last_stamped'] = {'$gte': since}
        elif before is not None:
            query['last_stamped'] = {'$lte': before}

        if minScore is not None:
            query['score'] = {'$gte' : minScore}

        return query

    def getPopularStampIds(self, **kwargs):
        key = str("fn::MongoStampCollection.getPopularStampIds::%s" % generateKeyFromDictionary(kwargs))
        try:
            return self._cache[key]
        except KeyError:
            pass

        limit = kwargs.pop('limit', 0)
        
        query = self._buildPopularQuery(**kwargs)

        documents = self._collection.find(query, fields=['_id']) \
                        .sort([('score', pymongo.DESCENDING)]) \
                        .limit(limit)

        result = map(lambda x: self._getStringFromObjectId(x['_id']), documents)

        cacheLength = 60 * 10 # 10 minutes
        try:
            self._cache.set(key, result, time=cacheLength)
        except Exception as e:
            logs.warning("Unable to set cache for key '%s': %s" % (key, e))

        return result

    def getPopularStampStats(self, **kwargs):
        limit = kwargs.pop('limit', 0)

        query = self._buildPopularQuery(**kwargs)

        documents = self._collection.find(query) \
                        .sort([('score', pymongo.DESCENDING)]) \
                        .limit(limit)

        return map(self._convertFromMongo, documents)



class MongoWhitelistedTastemakerStampIdsCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='tastemaker_whitelist', overflow=True)

    ### PUBLIC
    
    def getStampIds(self):
        documents = self._collection.find()
        return map(lambda x: x['stamp_id'], documents)

