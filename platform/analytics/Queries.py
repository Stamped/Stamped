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
from api.MongoStampedAPI import MongoStampedAPI
from boto.sdb.connection    import SDBConnection
from boto.exception         import SDBResponseError
from api.db.mongodb.MongoStatsCollection            import MongoStatsCollection
from bson.code import Code

#This file contains all analytics queries supported by the Stats.py module


api = MongoStampedAPI()
collection = api._userDB._collection

def totalFriends():
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

    
def newStamps(t0,t1):
    collection = api._stampDB._collection
    field = 'timestamp.created'
    return collection.find({field: {"$gte": t0,"$lte": t1 }}).count()

def newAccounts(t0,t1):
    collection = api._userDB._collection
    field = "timestamp.created"
    return collection.find({field: {"$gte": t0,"$lte": t1 }}).count()
    
