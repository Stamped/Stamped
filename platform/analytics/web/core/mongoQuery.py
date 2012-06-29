#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals
import argparse
import sys
import datetime
import calendar
import pprint
import keys.aws, logs, utils
from MongoStampedAPI import MongoStampedAPI
from boto.sdb.connection    import SDBConnection
from boto.exception         import SDBResponseError
from db.mongodb.MongoStatsCollection            import MongoStatsCollection
from bson.code import Code

#This file contains all analytics queries supported by the Stats.py module


class mongoQuery(object):
    
    def __init__(self):
        utils.init_db_config('peach.db2')
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
    
    def customQuery(self,t0,t1,collection,field,types=None):
        if types is None:
            return collection.find({field: {"$gte": t0, "$lte": t1}}).count()
        else:
            output = []
            for type in types:
                output.append(collection.find({field: {"$gte": t0, "$lte": t1}, 'entity.types': type }).count())
                return output
