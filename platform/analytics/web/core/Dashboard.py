#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals


<<<<<<< HEAD
import keys.aws, logs, utils, math

from analytics_utils        import *
from MongoStampedAPI        import MongoStampedAPI
from logsQuery              import logsQuery
from gevent.pool            import Pool
from statWriter             import statWriter
from boto.sdb.connection    import SDBConnection

class Dashboard(object):
    
    def __init__(self,api=MongoStampedAPI(),logsQuery=logsQuery()):
        self.stamp_collection = api._stampDB._collection
        self.acct_collection = api._userDB._collection
        self.query = logsQuery
        self.writer = statWriter('dashboard')
        conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
        self.domain = conn.get_domain('dashboard')
=======
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
>>>>>>> 94513bd8d4cb04bbe26209c9ffce1c2ba4455dd8
        
    def getStats(self,stat,fun,unique=False):
        total_today = 0
        today_hourly = []
        for hour in range (0,int(math.floor(est().hour))+1):
            if unique:
                bgn = today()
            else:
                bgn = today() + timedelta(hours=hour)
            end = today() + timedelta(hours=hour+1)
            num = fun(bgn,end)
            if not unique:
                total_today += num
            else:
                total_today = num
            today_hourly.append(total_today)
            
        
        total_yest = 0
        yest_hourly = []
        
        query = self.domain.select('select hours from `dashboard` where stat = "%s" and time = "day" and bgn = "%s"' % (stat,yesterday(today()).date().isoformat()))
        for result in query:
            for i in result['hours'].replace('[','').replace(']','').split(','):
                try:
                    yest_hourly.append(int(i))
                except:
                    pass
            print yest_hourly
        if len(yest_hourly) == 0:
            for hour in range (0,24):
                if unique:
                    bgn = yesterday(today())
                else:
                    bgn = yesterday(today()) + timedelta(hours=hour)
                end = yesterday(today()) + timedelta(hours=hour+1)
                num = fun(bgn,end)
                if not unique:
                    total_yest += num
                else:
                    total_yest = num
                yest_hourly.append(total_yest)
            print yest_hourly
            self.writer.write({'stat': stat,'time':'day','bgn':yesterday(today()).date().isoformat(),'hours':str(yest_hourly)})
        
        
        
        weeklyAgg = []
        weeklyAvg = []
        bgn = weekAgo(today())
        end = bgn + timedelta(hours=1)
        query = self.domain.select('select hours from `dashboard` where stat = "%s" and time = "week" and bgn = "%s"' % (stat,weekAgo(today()).date().isoformat()))
        for result in query:
            for i in result['hours'].replace('[','').replace(']','').split(','):
                try:
                    weeklyAvg.append(float(i))
                except:
                    pass
        if len(weeklyAvg) == 0: 
            for day in range (0,6):
                daily = 0
                if unique and day > 0:
                    bgn = bgn + timedelta(days=1) 
                for hour in range (0,24):
                    num = fun(bgn,end)
                    if not unique:
                        daily += num
                        bgn = bgn + timedelta(hours=1)
                    else:
                        daily = num
                    end = end + timedelta(hours = 1)
                    try:
                        weeklyAgg[hour] += daily
                    except Exception:
                        weeklyAgg.append(daily)
                
            for hour in range (0,len(weeklyAgg)):
                weeklyAvg.append(weeklyAgg[hour] / 6.0)
            self.writer.write({'stat': stat,'time':'week','bgn':weekAgo(today()).date().isoformat(),'hours':str(weeklyAvg)})
        
        
        try:
            deltaDay = float(total_today - yest_hourly[int(math.floor(est().hour))])/(yest_hourly[int(math.floor(est().hour))])*100.0
        except ZeroDivisionError:
            deltaDay = 'N/A'
        
        try: 
            deltaWeek = float(total_today - weeklyAvg[int(math.floor(est().hour))])/(weeklyAvg[int(math.floor(est().hour))])*100
        except ZeroDivisionError:
            deltaWeek = 'N/A'
        
        
        return today_hourly,total_today,yest_hourly,yest_hourly[int(math.floor(now().hour))],weeklyAvg,weeklyAvg[int(math.floor(now().hour))],deltaDay,deltaWeek
    
    def newStamps(self):
        fun = (lambda bgn,end: self.stamp_collection.find({'timestamp.created': {'$gte': bgn,'$lt': end}}).count())
        return self.getStats('stamps',fun)
    
    def newAccounts(self):
        fun = (lambda bgn,end: self.acct_collection.find({'timestamp.created': {'$gte': bgn,'$lt': end}}).count())
        return self.getStats('accts',fun)
    
    def todaysUsers(self):
        fun = (lambda bgn,end: self.query.activeUsers(bgn, end))
        return self.getStats('users',fun,True)
    

        
        
    
    

