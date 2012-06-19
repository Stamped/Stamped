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
from Entity                             import buildEntity

from api.AStampDB                       import AStampDB
from AMongoCollection                   import AMongoCollection
from AMongoCollectionView               import AMongoCollectionView
from MongoUserLikesCollection           import MongoUserLikesCollection
from MongoUserLikesHistoryCollection    import MongoUserLikesHistoryCollection
from MongoStampLikesCollection          import MongoStampLikesCollection
from MongoStampViewsCollection          import MongoStampViewsCollection
from MongoUserStampsCollection          import MongoUserStampsCollection
from MongoInboxStampsCollection         import MongoInboxStampsCollection
from MongoDeletedStampCollection        import MongoDeletedStampCollection
from MongoCreditGiversCollection        import MongoCreditGiversCollection
from MongoCreditReceivedCollection      import MongoCreditReceivedCollection

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
    
    def _convertFromMongo(self, document):
        if document is None:
            return None
        
        if '_id' in document and self._primary_key is not None:
            document[self._primary_key] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])

        # Convert single-blurb documents into new multi-blurb schema
        if 'stamped' not in document['timestamp']:
            if 'created' in document['timestamp']:
                created = document['timestamp']['created']
            else:
                try:
                    created = ObjectId(document[self._primary_key]).generation_time.replace(tzinfo=None)
                except Exception:
                    logs.warning("Unable to convert ObjectId to timestamp")
                    created = datetime.utcnow()
            contents =  {
                'blurb'     : document.pop('blurb', None),
                'mentions'  : document.pop('mentions', None),
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
                                'url'       : 'http://static.stamped.com/stamps/%s.jpg' % document['stamp_id'],
                            }
                        ]
                    }
                ]
            document['contents'] = [ contents ]
            document['timestamp']['stamped'] = created

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

        entityData = document.pop('entity')
        entity = buildEntity(entityData)
        document['entity'] = {'entity_id': entity.entity_id}
        
        stamp = self._obj().dataImport(document, overflow=self._overflow)
        stamp.entity = entity

        return stamp 
    
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
    
    ### DEPRECATED: 5/22/12
    def getStampsSlice(self, stampIds, genericCollectionSlice):
        if stampIds is not None:
            if len(stampIds) == 0:
                return []
            
            ids     = map(self._getObjectIdFromString, stampIds)
            
            if len(ids) == 1:
                query   = { '_id' : ids[0] }
            else:
                query   = { '_id' : { '$in' : ids } }
        else:
            query   = { }
        
        return self._getSlice(query, genericCollectionSlice)
    
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
    
    def getStampsSliceForEntity(self, entityId, genericCollectionSlice, userIds=None):
        query = {'entity.entity_id': entityId}

        if userIds is not None:
            if len(userIds) == 0:
                return []
            
            if len(userIds) == 1:
                query['user.user_id'] = userIds[0]
            else:
                query['user.user_id'] = { '$in' : userIds }

        return self._getSlice(query, genericCollectionSlice)

    def getStampsForEntity(self, entityId, limit=None):
        try:
            docs = self._collection.find({
                'entity.entity_id': entityId,
            })
            if limit is not None:
                docs = docs.limit(limit)
            
            return list(self._convertFromMongo(doc) for doc in docs)
        except Exception:
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
    
    def giveCredit(self, creditedUserId, stamp):
        # Add to 'credit received'
        ### TODO: Does this belong here?
        self.credit_received_collection.addCredit(creditedUserId, stamp.stamp_id)
        
        # Add to 'credit givers'
        ### TODO: Does this belong here?
        self.credit_givers_collection.addGiver(creditedUserId, stamp.user.user_id)
    
    def removeCredit(self, creditedUserId, stamp):
        # Add to 'credit received'
        ### TODO: Does this belong here?
        self.credit_received_collection.removeCredit(creditedUserId, stamp.stamp_id)
        
        # Add to 'credit givers'
        ### TODO: Does this belong here?
        self.credit_givers_collection.removeGiver(creditedUserId, stamp.user.user_id)

    def checkCredit(self, creditedUserId, stamp):
        credits = self.credit_received_collection.getCredit(creditedUserId)
        if stamp.stamp_id in credits:
            return True
        return False 
    
    def countCredits(self, userId):
        return self.credit_received_collection.numCredit(userId)

    def getRestamps(self, userId, entityId, limit=0):
        try:
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
        documentIds = []
        for stampId in stampIds:
            documentIds.append(self._getObjectIdFromString(stampId))
        result = self._removeMongoDocuments(documentIds)
        
        return result

