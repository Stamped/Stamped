#!/usr/bin/python

__author__ = 'Stamped (dev@stamped.com)'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__ = 'TODO'

import Globals
import copy

from threading import Lock
from datetime import datetime

from MongoDB import Mongo
# from api.AFriendshipDB import AFriendshipDB
# from api.Friendship import Friendship

class MongoUserFavorites(Mongo):
        
    COLLECTION = 'userfavorites'
        
    SCHEMA = {
        '_id': basestring,
        'favorite_id': basestring
    }
    
    def __init__(self, setup=False):
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
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


    ### PRIVATE
    
