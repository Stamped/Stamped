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
from bson.objectid import ObjectId
from analytics_utils import *

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
    
    def usersFollowingNonSuggested(self,version="v2"):
        if version not in ["v1","v2"]:
            return 0
        # All users following at least one person who is not a suggested user
        users = self.api._friendshipDB.friends_collection._collection.find({'ref_ids': {'$elemMatch': {'$nin': ['4ff72c599713965571000984',
                                                                                                               '4ff2279797139655710004bb',
                                                                                                               '4ff72cd097139667e50001c8',
                                                                                                               '4ff72d3a9713960355000509',
                                                                                                               '4f590e37b951fe37730005ad',
                                                                                                               '4ff48142d56d834b79000744',
                                                                                                               '4ff47ff0971396601500057c',
                                                                                                               '4e972d8dfe4a1d22d30002d1',
                                                                                                               '4e9b41f0fe4a1d44dd000601',
                                                                                                               '4ecc1f01e8ef215a42000339',
                                                                                                               '4e792021d6970356a5000042',
                                                                                                               '5011d981c5fc3e11461b6ee8',
                                                                                                               '500f3833d56d83787e000647',
                                                                                                               '4fc107f2b951fe2f75000d36',
                                                                                                               '4f567cdcd56d833b66000165',
                                                                                                               '4ecaedd2366b3c15540004f0',
                                                                                                               '4fe3721b9713967a5000007e',
                                                                                                               '4e8dfef6967ed34b3e00086c',
                                                                                                               '4e985cc7fe4a1d2fc4000220',
                                                                                                               '4f5279b5591fa45c3700053b']}}})
        user_ids = map(lambda x: ObjectId(x['_id']), users)
        
        if version == "v1":
            result = self.api._userDB._collection.find({'timestamp.created': {'$lt': v2_init()}, '_id': {'$in': user_ids}}).count()
        else:
            result = self.api._userDB._collection.find({'timestamp.created': {'$gte': v2_init()}, '_id': {'$in': user_ids}}).count()

        return result
        
        
        
        
        
        
        
        
        