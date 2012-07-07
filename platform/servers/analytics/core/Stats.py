#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals

import calendar, pprint, datetime, sys, argparse
import logs, utils, math


from boto.sdb.connection                    import SDBConnection
from boto.exception                         import SDBResponseError
from api.db.mongodb.MongoStatsCollection    import MongoStatsCollection
from gevent.pool                            import Pool
from servers.analytics.core.logsQuery           import logsQuery
from servers.analytics.core.mongoQuery          import mongoQuery
from servers.analytics.core.analytics_utils     import v1_init
 
class Stats():
    
    def __init__(self):
        self.mongoQ = mongoQuery()
        self.logsQ = logsQuery()
        
        self.evals = {
                 'stamps': self.mongoQ.newStamps,
                 'agg_stamps': (lambda t0,t1: self.mongoQ.newStamps(v1_init(),t1)),
                 'accounts': self.mongoQ.newAccounts,
                 'agg_accts': (lambda t0,t1: self.mongoQ.newAccounts(v1_init(),t1)),
                 'friendships': (lambda t0, t1: self.logsQ.customQuery(t0,t1,'count(*)','/v0/friendships/create.json')),
                 'users': self.logsQ.activeUsers,
                 'comments': (lambda t0, t1: self.logsQ.customQuery(t0,t1,'count(*)','/v0/comments/create.json')),
                 'todos': (lambda t0, t1: self.logsQ.customQuery(t0,t1,'count(*)','/v0/todos/create.json')),
                 'todos_c': (lambda t0, t1: self.logsQ.customQuery(t0,t1,'count(*)','/v0/todos/complete.json')),
                 'likes': (lambda t0, t1: self.logsQ.customQuery(t0,t1,'count(*)','/v0/stamps/likes/create.json')),
                 'entities': (lambda t0, t1: self.logsQ.customQuery(t0,t1,'count(*)','/v0/entities/create.json')),
                 'friends': (lambda t0, t1: self.logsQ.customQuery(v1_init(),t1,'count(*)','/v0/friendships/create.json')),
                 'actions': (lambda t0, t1: self.logsQ.customQuery(v1_init(),t1,'count(*)','/v0/actions/complete.json')),
                 }
    
    
    def perUser(self,computed):
        output = computed
        for i in range (0,len(computed)):
            t0,t1 = computed[i][0], computed[i][1]
            users = self.evals['users'](t0,t1)
            if users == 0:
                output[i][2] = 0
            else:
                output[i][2] = float(output[i][2])/users
        return output
        
    
    def query(self, scope, vital, bgn, end=None, perUser=False):
    
        _day = datetime.timedelta(hours=23, minutes=59, seconds=59,microseconds=999999)
        
        def incrMonth(date):
            succ = date.month
            year = date.year + succ / 12
            succ = succ % 12 + 1
            day = min(date.day,calendar.monthrange(year,succ)[1])
            return datetime.datetime(year,succ,day)
        
        if end == None:
            end = datetime.datetime.utcnow()
        
        prev = bgn
        agg=0
        output = []
        
        if scope == 'total':
            try:
                fun = self.evals[vital] 
                total = fun(bgn, end)
                output.append([bgn,end,total])
            except KeyError:
                print "Statistic not supported"
            
            if perUser:
                output = self.perUser(output)
                
            return output
        
        elif scope == 'day': 
            interval = int((end.date() - bgn.date()).days+1)
            succ = bgn + _day
            
        elif scope == 'week': 
            interval = int((end.date() - bgn.date()).days/(7)+1)
            succ = bgn + datetime.timedelta(days= (6-bgn.weekday())) + _day
            
        elif scope == 'month': 
            interval = ((end.year-bgn.year)*12 + end.month) - bgn.month +1
            days_left = calendar.monthrange(bgn.year, bgn.month)[1] - bgn.day
            succ = bgn + datetime.timedelta(days=days_left) + _day
        
        for i in range (1,interval+1):
            
            if prev != bgn:
                if scope == 'day':
                    succ = prev + _day
                elif scope == 'week':
                    succ = prev + datetime.timedelta(days=6) + _day
                elif scope == 'month':
                    succ = incrMonth(prev) + datetime.timedelta(microseconds=-1)
            
            if succ > end:
                succ = end
            
            try:
                fun = self.evals[vital] 
                total = fun(prev, succ)
            except KeyError:
                print "Statistic not supported"
            
            
            output.append([prev,succ,total])
            prev = succ + datetime.timedelta(microseconds=1)
            agg += total
        
        if perUser:
            output = self.perUser(output)

        
        return output
    
    def setupGraph(self,output):
        bgns = []
        ends = []
        values = []
        base = []
        
        count=0
        for entry in output:
            t0 = entry[0].date()
            t1 = (entry[1] + datetime.timedelta(microseconds=1)).date()
            
            try:
                if math.floor(entry[2]) != math.ceil(entry[2]):
                    value = '%.3f' % entry[2]
                else: 
                    value = int(entry[2])
            except:
                    value = entry[2]

            bgns.append("%s/%s" % (t0.month,t0.day))
            ends.append("%s/%s" % (t1.month,t1.day))
            values.append(value)
            base.append(count)
            count += 1
        return bgns,ends,values,base
    
        
        