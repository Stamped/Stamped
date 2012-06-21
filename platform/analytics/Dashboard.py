#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals


import keys.aws, logs, utils

from logsQuery                          import logsQuery
from MongoStampedAPI                    import MongoStampedAPI
from boto.sdb.connection                import SDBConnection
from boto.exception                     import SDBResponseError
from db.mongodb.MongoStatsCollection    import MongoStatsCollection
from gevent.pool                        import Pool
from datetime                           import datetime
from datetime                           import timedelta
 
api = MongoStampedAPI()
stamp_collection = api._stampDB._collection
acct_collection = api._userDB._collection

conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)


v1_init = datetime(2011,11,21)

def today():
    now =  datetime.today()
    diff = timedelta(days=0,hours=now.hour,minutes=now.minute,seconds=now.second,microseconds=now.microsecond)
    return now - diff


def totalStamps(): 
    total = stamp_collection.count()
    new = stamp_collection.find({'timestamp.created:': {'$gte': today()}}).count()
    delta = float(new) / (total - new) *100.0
    return (total,new,delta)

def totalAccounts():
    total = acct_collection.count()
    new = acct_collection.find({'timestamp.created:': {'$gte': today()}}).count()
    delta = float(new) / (total - new) *100.0
    return (total,new,delta)

def todaysUsers():
    query = logsQuery()
    users = logsQuery.activeUsers(query, today(), datetime.today())
    return users
    
    
while True:
    
    totalS,newS,deltaS = totalStamps()
    print "Total Stamps: %s" % totalS
    print "New Stamps Today: %s" % newS
    print "Change: %s%%\n\n" % deltaS
    
    totalA,newA,deltaA = totalAccounts()
    print "Total Accounts: %s" % totalS
    print "New Accounts Today: %s" % newS
    print "Change: %s%%\n\n" % deltaS
    
    users = todaysUsers()
    print "Unique users today: %s" % users
   
    
    #Show me the top stamped overall by vertical
    
    #Show me the top stamped this week by vertical
    
    raw_input("Press Enter to refresh...")




