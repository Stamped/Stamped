#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

import keys.aws, logs, ast
import libs.ec2_utils

from datetime                                   import timedelta
from utils                                      import lazyProperty
from servers.analytics.core.mongoQuery          import mongoQuery
from servers.analytics.core.logsQuery           import logsQuery
from servers.analytics.core.SimpleDBConnection  import SimpleDBCacheConnection
from servers.analytics.core.AnalyticsUtils      import est, estMidnight, dayBefore, weekBefore


IS_PROD  = libs.ec2_utils.is_prod_stack()

# An instantiation of a Dashboard used to calculate statistics for the Daily Overview tab
class Dashboard(object):
    
    def __init__(self, mongoQuery=mongoQuery(), logsQuery=logsQuery()):
        self.logsQ = logsQuery
        self.mongoQ = mongoQuery
        
    @lazyProperty
    def _cache(self):
        return SimpleDBCacheConnection('dashboard')
    
    # Calculates Daily Overview stats for today up until the current hour
    # Takes in a function "fun" which collects the stats that are not already stored in the cache
    def _getTodaysStats(self, stat, fun): 
        
        today_hourly = []
        
        key = '%s-day-%s' % (stat, estMidnight().date().isoformat())
        
        # See if we've stored data earlier
        cached = self._cache.lookup(key)
        if cached is not None:
            today_hourly = ast.literal_eval(cached['hours'])
        
        # Fill in missing stats up until the current hour (e.g. if it is currently 8:04, fill in stats thru 9:00)
        for hour in range (len(today_hourly), est().hour+2):
            bgn = estMidnight()
            end = estMidnight() + timedelta(hours=hour)
            total_today = fun(bgn, end)
            today_hourly.append(total_today)
        
            # Only store data for full hours (e.g. if it is currently 8:40, only store stats thru 8:00)
            # Also only write from a prod stack connection to prevent inaccurate data from being stored
            if hour == est().hour and IS_PROD:
                self._cache.store(key, {'hours': str(today_hourly)})
        
        return today_hourly
    
    # Calculates Daily Overview stats for a given day (CANNOT be used for current day)
    def _getDaysStats(self,stat,fun,date):
        
        # This is not the proper way to get today's stats
        if date == estMidnight():
            logs.debug("WARNING: For today's stats the proper function to be used is getTodaysStats, not getDaysStats")
            raise
        
        day_hourly = []
        
        key = '%s-day-%s' % (stat, date.date().isoformat())
        
        # See if we've stored data earlier
        cached = self._cache.lookup(key)
        if cached is not None:
            day_hourly = ast.literal_eval(cached['hours'])
        
        # If we didn't, or we stored less than a full 24 hours, rebuild all of this day's stats and save them (if on prod stack)
        if len(day_hourly) < 25:
            day_hourly = []
            bgn = estMidnight(date) # 0-hour EST
            for hour in range (0,25):
                end = bgn + timedelta(hours=hour)
                total_day = fun(bgn, end)
                day_hourly.append(total_day)
            if IS_PROD:
                self._cache.store(key, {'hours': str(day_hourly)})
                
        return day_hourly
    
    # Calculates totals at each hour as an average of the past 6 days' stats at those hours
    def _getWeeklyAvg(self,stat,fun):
        
        weeklyAgg = []
        weeklyAvg = []
        
        key = '%s-week-%s' % (stat, weekBefore(estMidnight()).date().isoformat())
        
        # See if we've stored data for this week earlier
        cached = self._cache.lookup(key)
        if cached is not None:
            weeklyAvg = ast.literal_eval(cached['hours'])
        
        # If not then compute and store
        if len(weeklyAvg) == 0: 
            for day in range (0,6):
                daily = 0
                bgn = weekBefore(estMidnight()) + timedelta(days=day) 
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
                self._cache.store(key, {'hours': str(weeklyAvg)})
        
        return weeklyAvg

        
    def getStats(self,stat,fun):
        
        # Get all the stats we need      
        today_hourly = self._getTodaysStats(stat,fun)
        yest_hourly = self._getDaysStats(stat,fun,dayBefore(estMidnight()))
        weeklyAvg = self._getWeeklyAvg(stat,fun)
        
        total_today = today_hourly[-1]
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
        
        return today_hourly, total_today, yest_hourly, yest_now, weeklyAvg, weekly_now, deltaDay, deltaWeek
    
    
    def newStamps(self):
        fun = (self.mongoQ.newStamps)
        return self.getStats('stamps',fun)
    
    def newAccounts(self):
        fun = (self.mongoQ.newAccounts)
        return self.getStats('accts',fun)
    
    def returningUsers(self):
        fun = (lambda bgn, end: self.logsQ.activeUsers(bgn,end) - self.mongoQ.newAccounts(bgn,end))
        return self.getStats('returning', fun)
    
    def activeUsers(self):
        fun = (lambda bgn, end: self.logsQ.activeUsers)
        return self.getStats('users',fun)
    

        
        
    
    

