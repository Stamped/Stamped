#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from abc import abstractmethod
from StampedAPI import StampedAPI

from db.mongodb.MongoAccount import MongoAccount
from db.mongodb.MongoEntity import MongoEntity
from db.mongodb.MongoUser import MongoUser
from db.mongodb.MongoStamp import MongoStamp
from db.mongodb.MongoComment import MongoComment
from db.mongodb.MongoFavorite import MongoFavorite
from db.mongodb.MongoCollection import MongoCollection
from db.mongodb.MongoFriendship import MongoFriendship
from db.mongodb.MongoActivity import MongoActivity

class MongoStampedAPI(StampedAPI):
    """
        Implementation of Stamped API atop MongoDB.
    """
    
    def __init__(self):
        StampedAPI.__init__(self, "MongoStampedAPI")
        
        self._accountDB    = MongoAccount()
        self._entityDB     = MongoEntity()
        self._userDB       = MongoUser()
        self._stampDB      = MongoStamp()
        self._commentDB    = MongoComment()
        self._favoriteDB   = MongoFavorite()
        self._collectionDB = MongoCollection()
        self._friendshipDB = MongoFriendship()
        self._activityDB   = MongoActivity()
        
        self._validate()

