#!/usr/bin/python

__author__ = 'Stamped (dev@stamped.com)'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__ = 'TODO'

import Globals

from AMongoCollection import AMongoCollection

class MongoUserFavoritesCollection(AMongoCollection):
    
    SCHEMA = {
        '_id': basestring,
        'favorite_id': basestring
    }
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='userfavorites')
    
    ### PUBLIC
    
    def addUserFavorite(self, userId, favoriteId):
        if not isinstance(userId, basestring) or not isinstance(favoriteId, basestring):
            raise KeyError("ID not valid")
        
        self._createRelationship(keyId=userId, refId=favoriteId)
        return True
    
    def removeUserFavorite(self, userId, favoriteId):
        return self._removeRelationship(keyId=userId, refId=favoriteId)
    
    def getUserFavoriteIds(self, userId):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(userId)

