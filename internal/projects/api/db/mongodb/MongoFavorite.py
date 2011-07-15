#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from threading import Lock
from datetime import datetime

from MongoDB import Mongo
from AFavoriteDB import AFavoriteDB
from Favorite import Favorite
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
        'user': {
            'user_id': basestring,
            'user_name': basestring
        },
        'stamp': {
            'stamp_id': basestring,
            'stamp_blurb': basestring,      # ??
            'stamp_timestamp': basestring,
            'stamp_user_id': basestring,    # ??
            'stamp_user_name': basestring,
            'stamp_user_img': basestring    # ??
        },
        'timestamp': basestring,
        'complete': bool
    }
    
    def __init__(self, setup=False):
        AFavoriteDB.__init__(self, self.DESC)
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def addFavorite(self, favorite):
        favoriteId = self._addDocument(favorite)
        MongoUserFavorites().addUserFavorite(favorite['user']['user_id'], favoriteId)
        return favoriteId
    
    def getFavorite(self, favoriteId):
        favorite = Favorite(self._getDocumentFromId(favoriteId))
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
    
    def getFavoriteIds(self, userId):
        return MongoUserFavorites().getUserFavoriteIds(userId)
    
    def getFavorites(self, userId):
        favorites = self._getDocumentsFromIds(self.getFavoriteIds(userId))
        result = []
        for favorite in favorites:
            favorite = Favorite(favorite)
            if favorite.isValid == False:
                raise KeyError("Favorite not valid")
            result.append(favorite)
        return result
        
    
#     def addUsers(self, users):
#         return self._addDocuments(users)
            
    
    ### PRIVATE
            
    