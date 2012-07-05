#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals


import keys.aws, logs, utils

from analytics.web.core.logsQuery                          import logsQuery
from api.MongoStampedAPI                    import MongoStampedAPI
from boto.sdb.connection                import SDBConnection
from boto.exception                     import SDBResponseError
from api.db.mongodb.MongoStatsCollection    import MongoStatsCollection
from datetime                           import datetime, timedelta
from analytics.web.core.topStamped                         import getTopStamped


utils.init_db_config('peach.db2')

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
        deltaDay = 0.0
    
    try: 
        deltaWeek = float(todays - weeklyAvg)/(weeklyAvg)*100
    except ZeroDivisionError:
        deltaWeek = 0.0
    
    
    return todays,yesterdays,weeklyAvg,deltaDay,deltaWeek

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
        
    weeklyAvg = weeklyAgg / 6.0
    
    try:
        deltaDay = float(todays - yesterdays)/(yesterdays)*100.0
    except ZeroDivisionError:
        deltaDay = 0.0
    
    try: 
        deltaWeek = float(todays - weeklyAvg)/(weeklyAvg)*100
    except ZeroDivisionError:
        deltaWeek = 0.0
    
    
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
        deltaDay = 0.0
    
    try: 
        deltaWeek = float(todays - weeklyAvg)/(weeklyAvg)*100
    except ZeroDivisionError:
        deltaWeek = 0.0
    
    return (todays,yesterdays,weeklyAvg,deltaDay,deltaWeek)
    



