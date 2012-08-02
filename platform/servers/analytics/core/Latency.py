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



class LatencyReport(object):
    
    def __init__(self,logsQuery=logsQuery()):
        self.logsQ = logsQuery
        conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
        self.writer = statWriter('latency',conn=conn)
        self.cache = conn.get_domain('latency')
    
    
    def _getTodaysLatency(self): 
        
        diffs_overall = {}
        errs_overall = {}
        
        # Build up until the current hour (e.g. if it is currently 8:04, fill in stats thru 9:00)
        for hour in range (1, est().hour+2):
            diffs_hourly = {}
            errs_hourly = {}
            cache_hit = False
            # See if we've stored hourly data earlier
            query = self.cache.select('select diffs,errs from `latency` where itemName() = "hour-%s-%s"' % (hour,today().date().isoformat()))
            for result in query:
                cache_hit = True
                try: 
                    diffs = ast.literal_eval(result['diffs'])
                    errs = ast.literal_eval(result['errs'])
                except ValueError:
                    cache_hit = False
                    break
                    
            if not cache_hit:
                diffs,errs = self.logsQ.latencyReport(today(),today() + timedelta(hours=hour))
                
                for key,value in diffs.items():
                    diffs_hourly[key] = value
                    try:
                        diffs_overall[key].extend(value)
                    except KeyError:
                        diffs_overall[key] = value
                
                for key,value in errs.items():
                    errs_hourly[key] = value
                    try:
                        errs_overall[key] += value
                    except KeyError:
                        errs_overall[key] = value
                        
            if hour <= est().hour:
                self.writer.writeLatency({'hour': hour, 'date': today().date().isoformat(), 'diffs': str(diffs_hourly), 'errs': str(errs_hourly)})
            
        return diffs_overall
#        for uri in self.statDict:
#            sum = 0
#            max = 0
#            for num in self.statDict[uri]:
#                sum += num
#                if num > max:
#                    max = num
#            mean = float(sum) / len(self.statDict[uri])
#            sorte = sorted(self.statDict[uri])
#            median = percentile(sorte,.5)
#            ninetieth = percentile(sorte,.9)
#            n = len(self.statDict[uri])
#            errors4 = 0
#            errors5 = 0
#            if uri+'-4' in self.statDict:
#                errors4 = self.statDict[uri+'-4']
#            if uri+'-5' in self.statDict:
#                errors5 = self.statDict[uri+'-5']
#            
#            self.statDict[uri] = '%.3f' % mean,'%.3f' % median,'%.3f' % ninetieth, '%.3f' % max, n, errors4,errors5
#                
#            bgn = today()
#            end = today() + timedelta(hours=hour)
#            total_today = fun(bgn, end)
#            today_hourly.append(total_today)
#        
#            # Only store data for full hours (e.g. if it is currently 8:40, only store stats thru 8:00)
#            # Also only write from a prod stack connection to prevent data misrepresentation
#            if hour == est().hour and IS_PROD:
#                self.writer.writeHours({'stat': stat, 'time': 'day', 'bgn': today().date().isoformat(), 'hours': str(today_hourly)})
#        
#        return total_today, today_hourly
    
    
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
    

        
        
    
    

