#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from threading import Lock
from datetime import datetime

from api.AFavoriteDB import AFavoriteDB
from api.Favorite import Favorite
from MongoDB import Mongo
from MongoUserFavorites import MongoUserFavorites

class MongoFavorite(AFavoriteDB, Mongo):
        
    COLLECTION = 'favorites'
        
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
        AFavoriteDB.__init__(self, self.DESC)
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def addFavorite(self, favorite):
        favoriteId = self._addDocument(favorite, 'favorite_id')
        MongoUserFavorites().addUserFavorite(favorite['user_id'], favoriteId)
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
        return MongoUserFavorites().getUserFavoriteIds(userId)
    
    def getFavorites(self, userId):
        favorites = self._getDocumentsFromIds(self.getFavoriteIDs(userId), 'favorite_id')
        result = []
        for favorite in favorites:
            favorite = Favorite(favorite)
            if favorite.isValid == False:
                raise KeyError("Favorite not valid")
            result.append(favorite)
        return result
            
    
    ### PRIVATE
    
