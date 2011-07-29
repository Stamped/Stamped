#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals

from AMongoCollection import AMongoCollection
from MongoUserFavorites import MongoUserFavorites
from api.AFavoriteDB import AFavoriteDB
from api.Favorite import Favorite

class MongoFavoriteCollection(AMongoCollection, AFavoriteDB):
    
    SCHEMA = {
        '_id': object,
        'entity': {
            'entity_id': basestring,
            'title': basestring,
            'coordinates': {
                'lat': float, 
                'lng': float
            },
            'category': basestring,
            'subtitle': basestring
        },
        'user_id': basestring,
        'stamp': {
            'stamp_id': basestring,
            'display_name': basestring
        },
        'timestamp': {
            'created': datetime,
            'modified': datetime
        },
        'complete': bool
    }
    
    def __init__(self, setup=False):
        AMongoCollection.__init__(self, collection'favorites')
        AFavoriteDB.__init__(self)
        
        self._favorites = MongoUserFavorites()
    
    ### PUBLIC
    
    def addFavorite(self, favorite):
        favoriteId = self._addDocument(favorite, 'favorite_id')
        self._favorites.addUserFavorite(favorite['user_id'], favoriteId)
        return favoriteId
    
    def getFavorite(self, favoriteId):
        favorite = Favorite(self._getDocumentFromId(favoriteId, 'favorite_id'))
        if favorite.isValid == False:
            raise KeyError("Favorite not valid")
        return favorite
        
    def removeFavorite(self, favoriteID):
        return self._removeDocument(favoriteID)
        
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
        return self._favorites.getUserFavoriteIds(userId)
    
    def getFavorites(self, userId):
        favorites = self._getDocumentsFromIds(self.getFavoriteIDs(userId), 'favorite_id')
        result = []
        for favorite in favorites:
            favorite = Favorite(favorite)
            if favorite.isValid == False:
                raise KeyError("Favorite not valid")
            result.append(favorite)
        return result

