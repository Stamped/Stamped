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
from AFavoriteDB import AFavoriteDB

from Schemas import *

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
    
    def removeFavorite(self, userId, entityId):
        try:
            self._collection.remove({'entity.entity_id': entityId, \
                                        'user_id': userId})
        except:
            logs.warning("Cannot remove document")
            raise Exception
    
    def getFavorite(self, userId, entityId):
        try:
            document = self._collection.find_one( \
                        {'entity.entity_id': entityId, 'user_id': userId})
            favorite = self._convertFromMongo(document)
            return favorite
        except:
            logs.warning("Cannot get document")
            raise Exception

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

