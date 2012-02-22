#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, pymongo

from datetime                       import datetime
from utils                          import lazyProperty

from AFavoriteDB                    import AFavoriteDB
from AMongoCollectionView           import AMongoCollectionView
from MongoUserFavEntitiesCollection import MongoUserFavEntitiesCollection
from Schemas                        import *

class MongoFavoriteCollection(AMongoCollectionView, AFavoriteDB):
    
    def __init__(self):
        AMongoCollectionView.__init__(self, collection='favorites', primary_key='favorite_id', obj=Favorite)
        AFavoriteDB.__init__(self)

        self._collection.ensure_index([('entity.entity_id', pymongo.ASCENDING), \
                                        ('user_id', pymongo.ASCENDING)])

        self._collection.ensure_index([('user_id', pymongo.ASCENDING), \
                                        ('timestamp.created', pymongo.DESCENDING)])
    
    ### PUBLIC
    
    @lazyProperty
    def user_fav_entities_collection(self):
        return MongoUserFavEntitiesCollection()
    
    def addFavorite(self, favorite):
        favorite = self._addObject(favorite)
        
        # Add links to favorite
        self.user_fav_entities_collection.addUserFavoriteEntity( \
            favorite.user_id, favorite.entity.entity_id)
        
        return favorite
    
    def removeFavorite(self, userId, entityId):
        try:
            self._collection.remove({'entity.entity_id': entityId, \
                                        'user_id': userId})
        
            # Remove links to favorite
            self.user_fav_entities_collection.removeUserFavoriteEntity( \
                userId, entityId)
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
    
    def getFavorites(self, userId, genericCollectionSlice):
        query = { '_id' : self._getObjectIdFromString(userId) }
        
        return self._getSlice(query, genericCollectionSlice)
    
    def countFavorites(self, userId):
        n = self._collection.find({'user_id': userId}).count()
        return n
    
    def getFavoriteEntityIds(self, userId):
        return self.user_fav_entities_collection.getUserFavoriteEntities(userId)
    
    def completeFavorite(self, entityId, userId, complete=True):
        try:
            self._collection.update(
                {'entity.entity_id': entityId, 'user_id': userId},
                {'$set': {'complete': complete}},
                safe=True
            )
        except:
            logs.warning("Cannot complete favorite")
            raise Exception

