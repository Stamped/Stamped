#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from abc import abstractmethod

class MongoStampedAPI(StampedAPI):
    """
        Implementation of Stamped API atop MongoDB.
    """
    
    def __init__(self):
        StampedAPI.__init__(self)
        
        self._accountDB    = MongoAccount()
        self._entityDB     = MongoEntity()
        self._userDB       = MongoUser()
        self._stampDB      = MongoStamp()
        self._commentDB    = MongoComment()
        self._favoriteDB   = MongoFavorite()
        self._collectionDB = MongoCollection()
        self._friendshipDB = MySQLFriendshipDB()
        
        self._validate()

