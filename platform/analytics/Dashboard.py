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
from topStamped                         import getTopStamped
 
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
    new = stamp_collection.find({'timestamp.created': {'$gte': today()}}).count()
    delta = float(new) / (total - new) *100.0
    return (total,new,delta)

def totalAccounts():
    total = acct_collection.count()
    new = acct_collection.find({'timestamp.created': {'$gte': today()}}).count()
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
    print "Total Accounts: %s" % totalA
    print "New Accounts Today: %s" % newA
    print "Change: %s%%\n\n" % deltaA
    
    users = todaysUsers()
    print "Unique users today: %s\n\n" % users
   
    print "Most Stamped Today:"
    dailyTop = getTopStamped(None,str(today().date()),stamp_collection)
    count = 1
    for i in dailyTop[0:25]:
        print "%s) %s: %s stamps" % (count, i['_id'], int(i['value']))
        count += 1
    
    print "\nTrending this Week:"
    past_week = today() - timedelta(days=6)
    weeklyTop = getTopStamped(None,str(past_week.date()),stamp_collection)
    count = 1
    for i in weeklyTop[0:25]:
        print "%s) %s" % (count, i['_id'])
        count += 1
    
    #Show me the top stamped this week by vertical
    
    raw_input("Press Enter to refresh...")




