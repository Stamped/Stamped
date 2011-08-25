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
        AMongoCollection.__init__(self, collection='favorites', primary_key='favorite_id', obj=Favorite)
        AFavoriteDB.__init__(self)
    
    ### PUBLIC
    
    @lazyProperty
    def user_favorites_collection(self):
        return MongoUserFavoritesCollection()
    
    def addFavorite(self, favorite):
        favorite = self._addObject(favorite)
        
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

