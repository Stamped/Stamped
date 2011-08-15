#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals

from utils import lazyProperty
from StampedAPI import StampedAPI

from db.mongodb.MongoAccountCollection import MongoAccountCollection
from db.mongodb.MongoEntityCollection import MongoEntityCollection
from db.mongodb.MongoPlacesEntityCollection import MongoPlacesEntityCollection
from db.mongodb.MongoUserCollection import MongoUserCollection
from db.mongodb.MongoStampCollection import MongoStampCollection
from db.mongodb.MongoCommentCollection import MongoCommentCollection
from db.mongodb.MongoFavoriteCollection import MongoFavoriteCollection
from db.mongodb.MongoCollectionCollection import MongoCollectionCollection
from db.mongodb.MongoFriendshipCollection import MongoFriendshipCollection
from db.mongodb.MongoActivityCollection import MongoActivityCollection

class MongoStampedAPI(StampedAPI):
    """
        Implementation of Stamped API atop MongoDB.
    """
    
    def __init__(self, **kwargs):
        StampedAPI.__init__(self, "MongoStampedAPI", **kwargs)
        
        #self._accountDB      = MongoAccountCollection()
        self._entityDB       = MongoEntityCollection()
        self._placesEntityDB = MongoPlacesEntityCollection()
        #self._userDB         = MongoUserCollection()
        #self._stampDB        = MongoStampCollection()
        #self._commentDB      = MongoCommentCollection()
        #self._favoriteDB     = MongoFavoriteCollection()
        #self._collectionDB   = MongoCollectionCollection()
        #self._friendshipDB   = MongoFriendshipCollection()
        #self._activityDB     = MongoActivityCollection()
        
        #self._validate()
    
    @lazyProperty
    def _accountDB(self):
        return MongoAccountCollection()

    #@lazyProperty
    #def _entityDB(self):
    #    return MongoEntityCollection()

    @lazyProperty
    def _userDB(self):
        return MongoUserCollection()

    @lazyProperty
    def _stampDB(self):
        return MongoStampCollection()

    @lazyProperty
    def _commentDB(self):
        return MongoCommentCollection()

    @lazyProperty
    def _favoriteDB(self):
        return MongoFavoriteCollection()

    @lazyProperty
    def _collectionDB(self):
        return MongoCollectionCollection()

    @lazyProperty
    def _friendshipDB(self):
        return MongoFriendshipCollection()

    @lazyProperty
    def _activityDB(self):
        return MongoActivityCollection()

