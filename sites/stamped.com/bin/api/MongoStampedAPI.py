#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from StampedAPI import StampedAPI

from db.mongodb.MongoAccountCollection import MongoAccountCollection
from db.mongodb.MongoEntityCollection import MongoEntityCollection
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
    
    def __init__(self):
        StampedAPI.__init__(self, "MongoStampedAPI")
        
        self._accountDB    = MongoAccountCollection()
        self._entityDB     = MongoEntityCollection()
        self._userDB       = MongoUserCollection()
        self._stampDB      = MongoStampCollection()
        self._commentDB    = MongoCommentCollection()
        self._favoriteDB   = MongoFavoriteCollection()
        self._collectionDB = MongoCollectionCollection()
        self._friendshipDB = MongoFriendshipCollection()
        self._activityDB   = MongoActivityCollection()
        
        self._validate()

