#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import bson, logs, pprint, pymongo, re

from datetime                           import datetime
from utils                              import lazyProperty
from api.Schemas                        import *
from api.Entity                             import buildEntity

from api.AStampDB                       import AStampDB
from api.db.mongodb.AMongoCollection                   import AMongoCollection
from api.db.mongodb.AMongoCollectionView               import AMongoCollectionView
from api.db.mongodb.MongoUserLikesCollection           import MongoUserLikesCollection
from api.db.mongodb.MongoUserLikesHistoryCollection    import MongoUserLikesHistoryCollection
from api.db.mongodb.MongoStampLikesCollection          import MongoStampLikesCollection
from api.db.mongodb.MongoStampViewsCollection          import MongoStampViewsCollection
from api.db.mongodb.MongoUserStampsCollection          import MongoUserStampsCollection
from api.db.mongodb.MongoInboxStampsCollection         import MongoInboxStampsCollection
from api.db.mongodb.MongoCreditGiversCollection        import MongoCreditGiversCollection
from api.db.mongodb.MongoCreditReceivedCollection      import MongoCreditReceivedCollection

class MongoStampCollection(AMongoCollectionView, AStampDB):
    
    def __init__(self):
        AMongoCollectionView.__init__(self, collection='stamps', primary_key='stamp_id', obj=Stamp, overflow=True)
        AStampDB.__init__(self)
        
        self._collection.ensure_index([('timestamp.modified', pymongo.ASCENDING)])
        self._collection.ensure_index([('timestamp.created', pymongo.ASCENDING)])
        self._collection.ensure_index([('timestamp.stamped', pymongo.ASCENDING)])
        self._collection.ensure_index([('entity.entity_id', pymongo.ASCENDING)])
        self._collection.ensure_index([('user.user_id', pymongo.ASCENDING), \
                                        ('entity.entity_id', pymongo.ASCENDING)])
        self._collection.ensure_index([('user.user_id', pymongo.ASCENDING), \
                                        ('stats.stamp_num', pymongo.ASCENDING)])

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
    
    def _convertFromMongo(self, document):
        if document is None:
            return None

        document = self._upgradeDocument(document)
        
        if '_id' in document and self._primary_key is not None:
            document[self._primary_key] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])

        entityData = document.pop('entity')
        entity = buildEntity(entityData)
        document['entity'] = {'entity_id': entity.entity_id}
        
        stamp = self._obj().dataImport(document, overflow=self._overflow)
        stamp.entity = entity

        return stamp 

    ### INTEGRITY

    def checkIntegrity(self, key, repair=True):
        document = self._getMongoDocumentFromId(key)

        modified = False
        
        assert document is not None

        # Update stamp to new structure
        if 'contents' not in document or 'credit' in document:
            logs.warning("Old stamp schema")
            document = self._upgradeDocument(document)
            modified = True

        # Verify that user exists
        userId = document['user']['user_id']
        if self._collection._database['users'].find({'_id' : self._getObjectIdFromString(userId)}).count() != 1:
            raise StampedDataError("User '%s' not found" % userId)

        # Verify that any credited users exist
        if 'credits' in document:
            credits = []
            for credit in document['credits']:
                creditedUserId = credit['user']['user_id']
                query = {'_id' : self._getObjectIdFromString(creditedUserId)}
                if self._collection._database['users'].find(query).count() == 1:
                    credits.append(credit)
                else:
                    modified = True
            if len(credits) > 0:
                document['credits'] = credit 
            else:
                del(document['credits'])

        # Verify that entity exists
        entityId = document['entity']['entity_id']
        entity = self._collection._database['entities'].find_one({'_id' : self._getObjectIdFromString(entityId)})
        if entity is None:
            raise StampedDataError("Entity '%s' not found" % entityId)

        # Check if entity has been tombstoned; update entity if so
        if 'tombstone_id' in entity['sources'] and entity['sources']['tombstone_id'] is not None:
            logs.warning("Stamp is tombstoned")
            newEntityId = entity['sources']['tombstone_id']
            newEntity = self._collection._database['entities'].find_one({'_id' : self._getObjectIdFromString(newEntityId)})
            if newEntity is None:
                raise StampedDataError("Entity '%s' not found" % newEntityId)

            document['entity'] = buildEntity(newEntity).minimize().dataExport()
            modified = True
        # Check if entity stub has been updated
        else:
            # Note: Because schema objects use tuples and documents use lists, we need to convert the
            # raw document into a schema object in order to do the comparison.
            entityMini = buildEntity(entity, mini=True)
            if buildEntity(document['entity'], mini=True) != entityMini:
                logs.warning("Upgrading entity mini")
                document['entity'] = entityMini.dataExport()
                modified = True

        stampNum = document['stats']['stamp_num']
        duplicateStamps = self._collection.find({'user.user_id' : userId, 'stats.stamp_num' : stampNum})
        if duplicateStamps.count() > 1:
            duplicateStamps.sort('timestamp.created', pymongo.ASCENDING)
            raise StampedDataError("Duplicate stamp numbers '%s' for user '%s'" % (stampNum, userId))

        if modified and repair:
            self._collection.update({'_id' : key}, stamp)

        return True

        # Check if temp_image_url exists -> kick off async process
        # Check that image[s] have dimensions
        # Verify image url exists?
        # Check if stats need to be updated?
        # Verify that user_id / stamp_num is unique


    
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
    def stamp_views_collection(self):
        return MongoStampViewsCollection()
    
    @lazyProperty
    def user_likes_collection(self):
        return MongoUserLikesCollection()
    
    @lazyProperty
    def user_likes_history_collection(self):
        return MongoUserLikesHistoryCollection()
    
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
        if sort in ['modified', 'created']:
            sort = 'timestamp.%s' % sort
        else:
            sort = 'timestamp.created'
        
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
            ### TODO: Index
            stampNum = int(stampNum)
            document = self._collection.find_one({
                'user.user_id': userId, 
                'stats.stamp_num': stampNum,
            })
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
            documents = self._collection.find(query).sort('$natural', pymongo.DESCENDING).limit(limit)
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
        
    def getStampLikesAcrossStamps(self, stampIds, limit=4):
        # Returns user ids that have "liked" the stamp
        userIds = self.stamp_likes_collection.getStampLikesAcrossStampIds(stampIds, limit=limit) 
        return map(self._getObjectIdFromString, userIds)
        
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
    
    def addView(self, userId, stampId):
        self.stamp_views_collection.addStampView(stampId, userId)
    
    def getStampViews(self, stampId):
        # Returns user ids that have viewed the stamp
        return self.stamp_views_collection.getStampViews(stampId) 
    
    def removeStamps(self, stampIds):
        if stampIds is None or len(stampIds) == 0:
            raise Exception("Must pass stampIds to delete!")
        documentIds = []
        for stampId in stampIds:
            documentIds.append(self._getObjectIdFromString(stampId))
        result = self._removeMongoDocuments(documentIds)
        
        return result

