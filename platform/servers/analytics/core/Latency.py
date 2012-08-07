#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals

import keys.aws, logs, utils, math
import ast

from boto.sdb.connection                            import SDBConnection
from servers.analytics.core.analytics_utils         import *
from servers.analytics.core.logsQuery               import logsQuery
from servers.analytics.core.statWriter              import statWriter
from gevent.pool                                    import Pool
from time import time



class LatencyReport(object):
    
    def __init__(self,logsQuery=logsQuery()):
        self.logsQ = logsQuery
        conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
        self.writer = statWriter('latency',conn=conn)
        self.cache = conn.get_domain('latency')
    
    
    def _getTodaysLatency(self): 
        
        # Build up until the current hour (e.g. if it is currently 8:04, fill in stats thru 9:00)
        for hour in range (1, est().hour+1):
            stats = {}
            diffs_hourly = {}
            errs_hourly = {}
            cache_hit = False
            t0 = time()
            # See if we've stored hourly data earlier
            query = self.cache.select('select * from `latency` where itemName() = "hour-%s-%s"' % (hour,today().date().isoformat()))
            for result in query:
                cache_hit = True
                for key, value in result.items():
                    stats[str(key)] = ast.literal_eval(str(value))
                t1 = time()
                print "Cache hit for hour %s. Extraction time: %s seconds" % (hour, t1 - t0)
            
            if not cache_hit:
                stats = self.logsQ.latencyReport(today() + timedelta(hours=hour - 1),today() + timedelta(hours=hour))
                t1 = time()
                print "Cache miss for hour %s. Extraction time: %s seconds" % (hour, t1 - t0)
            
                self.writer.writeLatency({'hour': hour, 'date': today().date().isoformat(), 'stats': stats})    
                t2 = time()
                print "Cache miss for hour %s. Write time: %s seconds" % (hour, t2 - t1)
            
        return stats
     
    
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
        return self.getStats('users',fun)
    

        
        
    
    

