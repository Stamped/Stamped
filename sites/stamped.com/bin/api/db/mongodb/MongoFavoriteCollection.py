#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals

from datetime import datetime
from utils import lazyProperty

from AMongoCollection import AMongoCollection
from MongoUserFavoritesCollection import MongoUserFavoritesCollection
from MongoActivityCollection import MongoActivityCollection
from MongoUserCollection import MongoUserCollection

from api.AFavoriteDB import AFavoriteDB
from api.Favorite import Favorite

class MongoFavoriteCollection(AMongoCollection, AFavoriteDB):
    
    def __init__(self, setup=False):
        AMongoCollection.__init__(self, collection='favorites')
        AFavoriteDB.__init__(self)
    
    def _convertToMongo(self, favorite):
        document = favorite.exportSparse()
        if 'favorite_id' in document:
            document['_id'] = self._getObjectIdFromString(document['favorite_id'])
            del(document['favorite_id'])
        return document

    def _convertFromMongo(self, document):
        if document != None and '_id' in document:
            document['favorite_id'] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])
        return Favorite(document)
    
    ### PUBLIC
    
    @lazyProperty
    def user_favorites_collection(self):
        return MongoUserFavoritesCollection()

    def addFavorite(self, favorite):
        document = self._convertToMongo(favorite)
        document = self._addMongoDocument(document)
        favorite = self._convertFromMongo(document)
        
        # Add link to favorite
        self.user_favorites_collection.addUserFavorite(favorite.user_id, \
                                                        favorite.favorite_id)

        return favorite
    
    def removeFavorite(self, entityId, userId):
        try:
            self._collection.remove({'entity.entity_id': entityId, \
                                        'user_id': userId})
        except:
            logs.warning("Cannot remove document")
            raise Exception
    
    def getFavorite(self, favoriteId):
        documentId = self._getObjectIdFromString(favoriteId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)

    def getFavorites(self, userId, **kwargs):
        params = {
            'since':    kwargs.pop('since', None),
            'before':   kwargs.pop('before', None), 
            'limit':    kwargs.pop('limit', 20),
            'sort':     'timestamp.created',
        }

        favoriteIds = self.user_favorites_collection.getUserFavoriteIds(userId)

        documentIds = []
        for favoriteId in favoriteIds:
            documentIds.append(self._getObjectIdFromString(favoriteId))

        # Get stamps
        documents = self._getMongoDocumentsFromIds(documentIds, **params)

        favorites = []
        for document in documents:
            favorites.append(self._convertFromMongo(document))

        return favorites
    
    def completeFavorite(self, entityId, userId, complete=True):
        try:
            self._collection.update(
                {'entity.entity_id': entityId, 'user_id': userId},
                {'$set': {'complete': complete}}
                )
        except:
            logs.warning("Cannot complete favorite")
            raise Exception



    
    @lazyProperty
    def activity_collection(self):
        return MongoActivityCollection()
    
    @lazyProperty
    def user_collection(self):
        return MongoUserCollection()
    
    def completeFavorite(self, favoriteId, complete=True):
        if not isinstance(complete, bool):
            raise TypeError("Not a bool!")
        return self._validateUpdate(
            self._collection.update(
                {'_id': self._getObjectIdFromString(favoriteId)}, 
                {'$set': {'complete': complete}},
                safe=True)
            )
            
    def getFavoriteIdForEntity(self, userId, entityId):
        return self._collection.find_one(
            {'user_id': userId, 'entity.entity_id': entityId})
    
    def getFavoriteIDs(self, userId):
        return self.user_favorites_collection.getUserFavoriteIds(userId)






    
    def addFavoriteOld(self, favorite):
        # Add favorite
        favoriteId = self._addDocument(favorite, 'favorite_id')
        favorite['favorite_id'] = favoriteId
        
        # Add link to favorite
        self.user_favorites_collection.addUserFavorite(favorite['user_id'], favoriteId)
        
        # Add activity (if referencing a stamp)
        if 'stamp' in favorite and 'stamp_id' in favorite.stamp:
            user = self.user_collection.getUser(favorite.user_id)
            self.activity_collection.addActivityForFavorite([favorite.stamp['user_id']], user, favorite)
        
        return favoriteId
    
    def getFavoriteOld(self, favoriteId):
        favorite = Favorite(self._getDocumentFromId(favoriteId, 'favorite_id'))
        if favorite.isValid == False:
            raise KeyError("Favorite not valid")
        return favorite
        
    def removeFavoriteOld(self, favoriteId):
        return self._removeDocument(favoriteId)
    
    def getFavoritesOld(self, userId):
        favorites = self._getDocumentsFromIds(self.getFavoriteIDs(userId), 'favorite_id')
        result = []
        for favorite in favorites:
            favorite = Favorite(favorite)
            if favorite.isValid == False:
                raise KeyError("Favorite not valid")
            result.append(favorite)
        return result

