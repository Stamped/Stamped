#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals

import keys.aws, logs, utils, math, time
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
     
        
    def getStats(self,stat,fun):
        
        """
        Today's Stats
        """
        
        total_today = 0
        today_hourly = []
        
        # See if we've stored data earlier
        query = self.domain.select('select hours from `dashboard` where itemName() = "%s-day-%s"' % (stat,today().date().isoformat()))
        for result in query:
            for i in result['hours'].replace('[','').replace(']','').split(','):
                today_hourly.append(int(i))
        
        # Build up until the current hour (e.g. if it is currently 8:04, fill in stats thru 9:00)
        for hour in range (len(today_hourly), est().hour+2):
            bgn = today()
            end = today() + timedelta(hours=hour)
            total_today = fun(bgn,end)
            today_hourly.append(total_today)
        
            # Only store data for full hours (e.g. if it is currently 8:40, only store stats thru 8:00)
            # Also only write from a bowser stack connection to prevent data corruption
            if hour == est().hour and IS_PROD:
                self.writer.writeHours({'stat': stat,'time':'day','bgn':today().date().isoformat(),'hours':str(today_hourly)})
        
        
        """
        Yesterday's Stats
        """
        
        total_yest = 0
        yest_hourly = []
        
        # See if we've stored data earlier
        query = self.domain.select('select hours from `dashboard` where itemName() = "%s-day-%s"' % (stat,dayAgo(today()).date().isoformat()))
        for result in query:
            for i in result['hours'].replace('[','').replace(']','').split(','):
                yest_hourly.append(int(i))
        
        # If we didn't, rebuild all of yesterday's stats and save them if on bowser
        if len(yest_hourly) == 0:
            for hour in range (0,25):
                bgn = dayAgo(today())
                end = dayAgo(today()) + timedelta(hours=hour)
                total_yest = fun(bgn,end)
                yest_hourly.append(total_yest)
            if IS_PROD:
                self.writer.writeHours({'stat': stat,'time':'day','bgn':dayAgo(today()).date().isoformat(),'hours':str(yest_hourly)})
        
        
        """
        Weekly Stats
        """
        
        weeklyAgg = []
        weeklyAvg = []
        
        # See if we've stored data earlier
        query = self.domain.select('select hours from `dashboard` where itemName() = "%s-week-%s"' % (stat,weekAgo(today()).date().isoformat()))
        for result in query:
            for i in result['hours'].replace('[','').replace(']','').split(','):
                weeklyAvg.append(float(i))
        
        # If not then compute and store
        if len(weeklyAvg) == 0: 
            for day in range (0,6):
                daily = 0
                bgn = weekAgo(today()) + timedelta(days=day) 
                for hour in range (0,25):
                    end = bgn + timedelta(hours=hour)
                    daily = fun(bgn,end)
                    try:
                        weeklyAgg[hour] += daily
                    except Exception:
                        weeklyAgg.append(daily)
            
            # Take the aggregate and make an average
            for hour in range (0,len(weeklyAgg)):
                weeklyAvg.append(weeklyAgg[hour] / 6.0)
            
            if IS_PROD:
                self.writer.writeHours({'stat': stat,'time':'week','bgn':weekAgo(today()).date().isoformat(),'hours':str(weeklyAvg)})
        
        
        
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
    

        
        
    
    

