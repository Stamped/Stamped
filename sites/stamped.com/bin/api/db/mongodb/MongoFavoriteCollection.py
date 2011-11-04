#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals

from datetime import datetime
from utils import lazyProperty

from AMongoCollection import AMongoCollection
from MongoUserFavEntitiesCollection import MongoUserFavEntitiesCollection
from AFavoriteDB import AFavoriteDB

from Schemas import *

class MongoFavoriteCollection(AMongoCollection, AFavoriteDB):
    
    def __init__(self, setup=False):
        AMongoCollection.__init__(self, collection='favorites', primary_key='favorite_id', obj=Favorite)
        AFavoriteDB.__init__(self)

        self._collection.ensure_index([('entity.entity_id', pymongo.ASCENDING), \
                                        ('user_id', pymongo.ASCENDING)])
    
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
    
    def getFavorites(self, userId, **kwargs):
        since       = kwargs.pop('since', None)
        before      = kwargs.pop('before', None)
        sort        = kwargs.pop('sort', None)
        limit       = kwargs.pop('limit', 0)

        ### TODO: Make sure this is indexed
        params = {'user_id': userId}
        
        if since != None and before != None:
            params['timestamp.created'] = {'$gte': since, '$lte': before}
        elif since != None:
            params['timestamp.created'] = {'$gte': since}
        elif before != None:
            params['timestamp.created'] = {'$lte': before}
        
        if sort != None:
            documents = self._collection.find(params).sort(sort, \
                pymongo.DESCENDING).limit(limit)
        else:
            documents = self._collection.find(params).limit(limit)
        
        favorites = []
        for document in documents:
            favorites.append(self._convertFromMongo(document))
        
        return favorites

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

