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

query = logsQuery()


v1_init = datetime(2011,11,21)

def now():
    return datetime.utcnow()

def today():
    now = datetime.utcnow()
    diff = timedelta(days=0,hours=now.hour,minutes=now.minute,seconds=now.second,microseconds=now.microsecond)
    return now - diff

def yesterday(date):
    return date - timedelta(days=1)

def weekAgo(date):
    return date - timedelta(days=6)

def newStamps():
    todays = stamp_collection.find({'timestamp.created': {'$gte': today()}}).count()
    yesterdays = stamp_collection.find({'timestamp.created': {'$gte': yesterday(today()), '$lt': yesterday(now())}}).count()
    
    
    weeklyAgg = yesterdays
    bgn = yesterday(today())
    end = yesterday(now())
    for i in range (0,5):
        bgn = yesterday(bgn)
        end = yesterday(end)
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
    
    
    return (todays,yesterdays,weeklyAvg,deltaDay,deltaWeek)

def newAccounts():
    todays = acct_collection.find({'timestamp.created': {'$gte': today()}}).count()
    yesterdays = acct_collection.find({'timestamp.created': {'$gte': yesterday(today()), '$lt': yesterday(now())}}).count()
    
    
    weeklyAgg = yesterdays
    bgn = yesterday(today())
    end = yesterday(now())
    for i in range (0,5):
        bgn = yesterday(bgn)
        end = yesterday(end)
        weeklyAgg += acct_collection.find({'timestamp.created': {'$gte': bgn, '$lt': end}}).count()
        print "%s thru %s: %s" % (bgn,end,weeklyAgg)
        
    weeklyAvg = weeklyAgg / 6.0
    
    try:
        deltaDay = float(todays - yesterdays)/(yesterdays)*100.0
    except ZeroDivisionError:
        deltaDay = 'N/A'
    
    try: 
        deltaWeek = float(todays - weeklyAvg)/(weeklyAvg)*100
    except ZeroDivisionError:
        deltaWeek = 'N/A'
    
    
    return (todays,yesterdays,weeklyAvg,deltaDay,deltaWeek)

def todaysUsers():
    todays = query.activeUsers(today(), now())
    yesterdays = query.activeUsers(yesterday(today()), yesterday(now()))
    
    weeklyAgg = yesterdays
    bgn = yesterday(today())
    end = yesterday(now())
    for i in range (0,5):
        bgn = yesterday(bgn)
        end = yesterday(end)
        weeklyAgg += query.activeUsers(bgn, end)
        
    weeklyAvg = weeklyAgg / 6.0
    
    try:
        deltaDay = float(todays - yesterdays)/(yesterdays)*100.0
    except ZeroDivisionError:
        deltaDay = 'N/A'
    
    try: 
        deltaWeek = float(todays - weeklyAvg)/(weeklyAvg)*100
    except ZeroDivisionError:
        deltaWeek = 'N/A'
    
    return (todays,yesterdays,weeklyAvg,deltaDay,deltaWeek)
    
    
while True:
    
    todays,yesterdays,weeklyAvg,deltaDay,deltaWeek = newStamps()
    
    print now()
    print "Stamps Today: %s" % todays
    print "Stamps Yesterday: %s" % yesterdays
    print "D2D Change: %s%%" % deltaDay
    print "Weekly Avg: %s" % weeklyAvg
    print "W2D Change: %s%%" % deltaWeek
    
    todays,yesterdays,weeklyAvg,deltaDay,deltaWeek = newAccounts()
    

    print "New Accounts Today: %s" % todays
    print "New Accounts Yesterday: %s" % yesterdays
    print "D2D Change: %s%%" % deltaDay
    print "Weekly Avg: %s" % weeklyAvg
    print "W2D Change: %s%%" % deltaWeek
    
    todays,yesterdays,weeklyAvg,deltaDay,deltaWeek = todaysUsers()
    

    print "Active Users Today: %s" % todays
    print "Active Users Yesterday: %s" % yesterdays
    print "D2D Change: %s%%" % deltaDay
    print "Weekly Avg: %s" % weeklyAvg
    print "W2D Change: %s%%" % deltaWeek
    
   
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




