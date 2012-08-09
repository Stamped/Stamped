#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals

import keys.aws, logs, utils, math
import libs.ec2_utils

from boto.sdb.connection                            import SDBConnection
from api.MongoStampedAPI                            import MongoStampedAPI
from servers.analytics.core.analytics_utils         import *
from servers.analytics.core.logsQuery               import logsQuery
from servers.analytics.core.statWriter              import statWriter
from gevent.pool                                    import Pool

IS_PROD  = libs.ec2_utils.is_prod_stack()

class Dashboard(object):
    
    def __init__(self,api=MongoStampedAPI(), logsQuery=logsQuery()):
        self.stamp_collection = api._stampDB._collection
        self.acct_collection = api._userDB._collection
        self.query = logsQuery
        self.writer = statWriter('dashboard')
        conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
        self.domain = conn.get_domain('dashboard')
    
    
    def _getTodaysStats(self,stat,fun): 
        
        total_today = 0
        today_hourly = []
        
        # See if we've stored data earlier
        query = self.domain.select('select hours from `dashboard` where itemName() = "%s-day-%s"' % (stat, today().date().isoformat()))
        for result in query:
            for i in result['hours'].replace('[','').replace(']','').split(','):
                today_hourly.append(int(i))
        
        # Build up until the current hour (e.g. if it is currently 8:04, fill in stats thru 9:00)
        for hour in range (len(today_hourly), est().hour+2):
            bgn = today()
            end = today() + timedelta(hours=hour)
            total_today = fun(bgn, end)
            today_hourly.append(total_today)
        
            # Only store data for full hours (e.g. if it is currently 8:40, only store stats thru 8:00)
            # Also only write from a prod stack connection to prevent data misrepresentation
            if hour == est().hour and IS_PROD:
                self.writer.writeHours({'stat': stat, 'time': 'day', 'bgn': today().date().isoformat(), 'hours': str(today_hourly)})
        
        return total_today, today_hourly
    
    
    def _getDaysStats(self,stat,fun,date):
        
        # This is not the proper way to get current day's stats
        if date == today():
            print "WARNING: For today's stats the proper function to be used is getTodaysStats"
            raise
        
        total_day = 0
        day_hourly = []
        
        # See if we've stored data earlier
        query = self.domain.select('select hours from `dashboard` where itemName() = "%s-day-%s"' % (stat, date.date().isoformat()))
        for result in query:
            for i in result['hours'].replace('[','').replace(']','').split(','):
                day_hourly.append(int(i))
        
        # If we didn't, or we stored less than a full 24 hours, rebuild all of this day's stats and save them (if on prod stack)
        if len(day_hourly) < 25:
            day_hourly = []
            bgn = today(date) # 0-hour EST
            for hour in range (0,25):
                end = bgn + timedelta(hours=hour)
                total_day = fun(bgn, end)
                day_hourly.append(total_day)
            if IS_PROD:
                self.writer.writeHours({'stat': stat,'time':'day','bgn':date.date().isoformat(),'hours':str(day_hourly)})
                
        return day_hourly
    
    
    def _getWeeklyAvg(self,stat,fun):
        
        weeklyAgg = []
        weeklyAvg = []
        
        # See if we've stored data for this week earlier
        query = self.domain.select('select hours from `dashboard` where itemName() = "%s-week-%s"' % (stat,weekAgo(today()).date().isoformat()))
        for result in query:
            for i in result['hours'].replace('[','').replace(']','').split(','):
                weeklyAvg.append(float(i))
        
        # If not then compute and store
        if len(weeklyAvg) == 0: 
            for day in range (0,6):
                daily = 0
                bgn = weekAgo(today()) + timedelta(days=day) 
                daily = self._getDaysStats(stat,fun,bgn)
                print bgn, daily
                for i in range (0,len(daily)):
                    try:
                        weeklyAgg[i] += daily[i]
                    except IndexError:
                        weeklyAgg.append(daily[i])
            
            # Take the aggregate and make an average
            for hour in range (0,len(weeklyAgg)):
                weeklyAvg.append(weeklyAgg[hour] / 6.0)
            
            if IS_PROD:
                self.writer.writeHours({'stat': stat,'time':'week','bgn':weekAgo(today()).date().isoformat(),'hours':str(weeklyAvg)})
        
        return weeklyAvg

    
    def getStats(self,stat,fun):
        
        # Get all the stats we need      
        total_today, today_hourly = self._getTodaysStats(stat,fun)
        yest_hourly = self._getDaysStats(stat,fun,dayAgo(today()))
        weeklyAvg = self._getWeeklyAvg(stat,fun)
        
        # Compute D/D and D/W changes
        yest_now = yest_hourly[est().hour] + est().minute * ((yest_hourly[est().hour + 1]) - (yest_hourly[est().hour])) / 60
        
        weekly_now = weeklyAvg[est().hour] + est().minute * ((weeklyAvg[est().hour + 1]) - (weeklyAvg[est().hour])) / 60
        
        try:
            deltaDay = ((total_today - yest_now) / float(yest_now)) * 100.0
        except ZeroDivisionError:
            deltaDay = 0.0
        
        try: 
            deltaWeek = ((total_today - weekly_now) / weekly_now) * 100
        except ZeroDivisionError:
            deltaWeek = 0.0
        
        return today_hourly,total_today,yest_hourly,yest_now,weeklyAvg,weekly_now,deltaDay,deltaWeek
    
    
    def newStamps(self):
        fun = (lambda bgn,end: self.stamp_collection.find({'timestamp.created': {'$gte': bgn,'$lt': end}}).count())
        return self.getStats('stamps',fun)
    
    
    def newAccounts(self):
        fun = (lambda bgn,end: self.acct_collection.find({'timestamp.created': {'$gte': bgn,'$lt': end}}).count())
        return self.getStats('accts',fun)


    def todaysUsers(self):
        fun = (lambda bgn, end: self.query.activeUsers(bgn, end))
        return self.getStats('users',fun)
    
    def returningUsers(self):
        fun = (lambda bgn, end: self.query.activeUsers(bgn,end) - self.acct_collection.find({'timestamp.created': {'$gte': bgn,'$lt': end}}).count())
        return self.getStats('returning', fun)
    

        
        
    
    

