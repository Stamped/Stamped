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

def now():
    return datetime.today()

def today():
    now = datetime.today()
    diff = timedelta(days=0,hours=now.hour,minutes=now.minute,seconds=now.second,microseconds=now.microsecond)
    return now - diff

def yesterday(date):
    return date - timedelta(days=1)

def weekAgo(date):
    return date - timedelta(days=6)

def totalStamps():
    todays = stamp_collection.find({'timestamp.created': {'$gte': today()}}).count()
    yesterdays = stamp_collection.find({'timestamp.created': {'$gte': yesterday(today()), '$lt': yesterday(now())}}).count()
    
    
    weeklyAgg = yesterdays
    bgn = yesterday(today())
    end = yesterday(now())
    for i in range (0,5):
        bgn = yesterday(bgn)
        end = yesterday(end)
        print bgn
        print end
        print weeklyAgg
        weeklyAgg += stamp_collection.find({'timestamp.created': {'$gte': bgn, '$lt': end}}).count()
        
    weeklyAvg = weeklyAgg / 6.0
    
    try:
        deltaDay = float(todays - yesterdays)/(yesterdays)*100.0
    except ZeroDivisionError:
        deltaDay = 'N/A'
    
    try: 
        deltaWeek = float(todays - weeklyAvg)/(weeklyAvg)*100
    except ZeroDivisionError:
        deltaWeek = 'N/A'
    
    
    return (now(),todays,yesterdays,weeklyAvg,deltaDay,deltaWeek)

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
    
    hour,todays,yesterdays,weeklyAvg,deltaDay,deltaWeek = totalStamps()
    
    print hour
    print "Stamps Today: %s" % todays
    print "Stamps Yesterday: %s" % yesterdays
    print "D2D Change: %s%%" % deltaDay
    print "Weekly Avg: %s" % weeklyAvg
    print "W2D Change: %s%%" % deltaWeek
    
#    totalA,newA,deltaA = totalAccounts()
#    print "Total Accounts: %s" % totalA
#    print "New Accounts Today: %s" % newA
#    print "Change: %s%%\n\n" % deltaA
#    
#    users = todaysUsers()
#    print "Unique users today: %s\n\n" % users
#   
#    print "Most Stamped Today:"
#    dailyTop = getTopStamped(None,str(today().date()),stamp_collection)
#    count = 1
#    for i in dailyTop[0:25]:
#        print "%s) %s: %s stamps" % (count, i['_id'], int(i['value']))
#        count += 1
#    
#    print "\nTrending this Week:"
#    past_week = today() - timedelta(days=6)
#    weeklyTop = getTopStamped(None,str(past_week.date()),stamp_collection)
#    count = 1
#    for i in weeklyTop[0:25]:
#        print "%s) %s" % (count, i['_id'])
#        count += 1
    
    #Show me the top stamped this week by vertical
    
    raw_input("Press Enter to refresh...")




