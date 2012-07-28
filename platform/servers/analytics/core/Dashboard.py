#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals

import keys.aws, logs, utils, math, time

from boto.sdb.connection                            import SDBConnection
from api.MongoStampedAPI                            import MongoStampedAPI
from servers.analytics.core.analytics_utils         import *
from servers.analytics.core.logsQuery               import logsQuery
from servers.analytics.core.statWriter              import statWriter
from gevent.pool                                    import Pool

class Dashboard(object):
    
    def __init__(self,api=MongoStampedAPI(),logsQuery=logsQuery()):
        self.stamp_collection = api._stampDB._collection
        self.acct_collection = api._userDB._collection
        self.query = logsQuery
        self.writer = statWriter('dashboard')
        conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
        self.domain = conn.get_domain('dashboard')
        
    def getStats(self,stat,fun,unique=False):
        
        # Today's Stats
        total_today = 0
        today_hourly = [0]
        
        query = self.domain.select('select hours from `dashboard` where stat = "%s" and time = "day" and bgn = "%s"' % (stat,today().date().isoformat()))

        for result in query:
            for i in result['hours'].replace('[','').replace(']','').split(','):
                today_hourly.append(int(i))
        

        for hour in range (len(today_hourly), est().hour+2):
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

            self.writer.write({'stat': stat,'time':'day','bgn':today().date().isoformat(),'hours':str(today_hourly)})
            
            total_today = today_hourly[-1]
        
        
        # Yesterday's Stats
        total_yest = 0
        yest_hourly = [0]
        
        query = self.domain.select('select hours from `dashboard` where stat = "%s" and time = "day" and bgn = "%s"' % (stat,dayAgo(today()).date().isoformat()))

        for result in query:
            for i in result['hours'].replace('[','').replace(']','').split(','):
                try:
                    yest_hourly.append(int(i))
                except:
                    pass
        
        if len(yest_hourly) == 1:
            for hour in range (0,24):
                if unique:
                    bgn = dayAgo(today())
                else:
                    bgn = dayAgo(today()) + timedelta(hours=hour)
                end = dayAgo(today()) + timedelta(hours=hour+1)
                num = fun(bgn,end)
                if not unique:
                    total_yest += num
                else:
                    total_yest = num
                yest_hourly.append(total_yest)

            self.writer.write({'stat': stat,'time':'day','bgn':dayAgo(today()).date().isoformat(),'hours':str(yest_hourly)})
        
        
        # Weekly Avg Stats
        weeklyAgg = [0]
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
            deltaDay = 0.0
        
        try: 
            deltaWeek = float(total_today - weeklyAvg[int(math.floor(est().hour))])/(weeklyAvg[int(math.floor(est().hour))])*100
        except ZeroDivisionError:
            deltaWeek = 0.0
        
        return today_hourly,total_today,yest_hourly,yest_hourly[int(math.floor(est().hour))],weeklyAvg,weeklyAvg[int(math.floor(est().hour))],deltaDay,deltaWeek
    
    def newStamps(self):
        fun = (lambda bgn,end: self.stamp_collection.find({'timestamp.created': {'$gte': bgn,'$lt': end}}).count())
        return self.getStats('stamps',fun)
    
    def newAccounts(self):
        fun = (lambda bgn,end: self.acct_collection.find({'timestamp.created': {'$gte': bgn,'$lt': end}}).count())
        return self.getStats('accts',fun)
    
    def todaysUsers(self):
        fun = (lambda bgn,end: self.query.activeUsers(bgn, end))
        return self.getStats('users',fun,True)
    

        
        
    
    

