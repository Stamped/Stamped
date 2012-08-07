#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals
import sys
import datetime
import calendar
import pprint
import pymongo
import keys.aws, logs, utils
from api.MongoStampedAPI import MongoStampedAPI
from boto.sdb.connection    import SDBConnection
from boto.exception         import SDBResponseError
from api.db.mongodb.MongoStatsCollection            import MongoStatsCollection
from bson.code import Code

#This file contains all analytics queries supported by the Stats.py module


class mongoQuery(object):
    
    def __init__(self,api=None):
        # utils.init_db_config('peach.db3')
        self.api = api
        if self.api is None:
            self.api = MongoStampedAPI()
    
    def totalFriends(self):
        collection = self.api._userDB._collection
        map = Code("function () {"
                   "if (this.stats.num_friends) {"
                   "emit(1,this.stats.num_friends)} "
                   ";}")
        
        reduce = Code("function (key,values) {"
                      "  var total = 0;"
                      "  for (var i = 0; i < values.length; i++) {"
                      "    total += values[i];"
                      "  }"
                      "  return total;"
                      "}")
        
        result = collection.inline_map_reduce(map, reduce)
        return result
    
        
    def newStamps(self,t0,t1):
        collection = self.api._stampDB._collection
        field = 'timestamp.created'
        return collection.find({field: {"$gte": t0,"$lte": t1 }}).count()
    
    def newAccounts(self,t0,t1):
        collection = self.api._userDB._collection
        field = "timestamp.created"
        return collection.find({field: {"$gte": t0,"$lte": t1 }}).count()
    
    def topUsers(self,limit):
        top_followed = self.api._userDB._collection.find().sort('stats.num_followers', pymongo.DESCENDING).limit(limit)
        results = []
        for user in top_followed:
            results.append((str(user['screen_name']), str(user['stats']['num_followers'])))
        return results
    
    def customQuery(self,t0,t1,collection,field,types=None):
        if types is None:
            return collection.find({field: {"$gte": t0, "$lte": t1}}).count()
        else:
            output = []
            for type in types:
                output.append(collection.find({field: {"$gte": t0, "$lte": t1}, 'entity.types': type }).count())
                return output
            
    def countMutualRelationships(self):
        user_ids = self.api._userDB._getAllUserIds()
        count = 0
        for user_id in user_ids:
            friends = self.api._friendshipDB.getFriends(user_id)
            followers = self.api._friendshipDB.getFollowers(user_id)
            for friend in friends:
                if friend in followers:
                    count += 1
                    break
        
        return count
            
        
        
        
        
        
        