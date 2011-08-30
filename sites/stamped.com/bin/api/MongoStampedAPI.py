#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
from Entity import *

from utils import lazyProperty
from StampedAPI import StampedAPI
from Schemas import *
from S3ImageDB import S3ImageDB

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
from db.mongodb.MongoEntitySearcher import MongoEntitySearcher

class MongoStampedAPI(StampedAPI):
    """
        Implementation of Stamped API atop MongoDB.
    """
    
    def __init__(self, db=None, **kwargs):
        StampedAPI.__init__(self, "MongoStampedAPI", **kwargs)
        
        if db:
            utils.init_db_config(db)
        
        self._entityDB       = MongoEntityCollection()
        self._placesEntityDB = MongoPlacesEntityCollection()
    
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
    
    @lazyProperty
    def _entitySearcher(self):
        return MongoEntitySearcher()
    
    @lazyProperty
    def _imageDB(self):
        return S3ImageDB()
    
    def getStats(self):
        source_stats = { }
        subcategory_stats = { }
        
        for source in EntitySourcesSchema()._elements:
            count = self._entityDB._collection.find({"sources.%s" % source : { "$exists" : True }}).count()
            source_stats[source] = count
        
        for subcategory in subcategories:
            count = self._entityDB._collection.find({"subcategory" : subcategory}).count()
            subcategory_stats[subcategory] = count
        
        stats = {
            'entities' : {
                'count' : self._entityDB._collection.count(), 
                'sources' : source_stats, 
                'subcategory' : subcategory_stats, 
                'places' : {
                    'count' : self._placesEntityDB._collection.count(), 
                }, 
            }, 
            'users' : {
                'count' : self._userDB._collection.count(), 
            }, 
            'comments' : {
                'count' : self._commentDB._collection.count(), 
            }, 
            'stamps' : {
                'count' : self._stampDB._collection.count(), 
            }, 
        }
        
        return stats

