#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals

import calendar, datetime, sys
import logs, utils, math

from datetime                               import timedelta
from servers.analytics.core.logsQuery       import logsQuery
from servers.analytics.core.mongoQuery      import mongoQuery
from servers.analytics.core.AnalyticsUtils  import v1_init, incrMonth
 
class CustomStatFinder():
    
    def __init__(self, mongoQuery=mongoQuery(), logsQuery=logsQuery()):
        self.mongoQ = mongoQuery
        self.logsQ = logsQuery
        
        # Dict of all supported queries
        self.evals = {
                 # Mongodb queries
                 'stamps': self.mongoQ.newStamps,
                 'agg_stamps': (lambda bgn, end: self.mongoQ.newStamps(v1_init(), end)),
                 'accounts': self.mongoQ.newAccounts,
                 'agg_accts': (lambda bgn, end: self.mongoQ.newAccounts(v1_init(), end)),
                 
                 # Simpledb queries
                 'users': (lambda bgn, end: self.logsQ.customQuery('users', [], bgn, end)),
                 'friendships': (lambda bgn, end: self.logsQ.customQuery('friendships', ['uri="/v1/friendships/create.json"'], bgn, end)),
                 'comments': (lambda bgn, end: self.logsQ.customQuery('comments', ['uri="/v1/comments/create.json"'], bgn, end)),
                 'todos': (lambda bgn, end: self.logsQ.customQuery('todos', ['uri="/v1/todos/create.json"'], bgn, end)),
                 'todos_c': (lambda bgn, end: self.logsQ.customQuery('todos_completed', ['uri="/v1/todos/complete.json"'], bgn, end)),
                 'likes': (lambda bgn, end: self.logsQ.customQuery('likes', ['uri="/v1/stamps/likes/create.json"'], bgn, end)),
                 'entities': (lambda bgn, end: self.logsQ.customQuery('entities_created', ['uri="/v1/entities/create.json"'], bgn, end)),
                 'friends': (lambda bgn, end: self.logsQ.customQuery('friends', ['uri="/v1/friendships/create.json"'], v1_init(), end)),
                 'actions': (lambda bgn, end: self.logsQ.customQuery('acions', ['uri="/v1/actions/complete.json"'], bgn, end)),
                 'return_users': (lambda bgn, end: self.logsQ.customQuery('users', [], bgn, end) - self.mongoQ.newAccounts(bgn, end))
                 }
    
    # Divide the output of a given query by the number of daily users to get a per-user figure
    def perUser(self, computed):
        output = computed
        for i in range (len(computed)):
            bgn, end = computed[i][0], computed[i][1]
            users = self.evals['users'](bgn, end)
            if users == 0:
                output[i][2] = 0
            else:
                output[i][2] = float(output[i][2]) / users
        return output
        
    
    def query(self, scope, stat, bgn, end=None, perUser=False):
        
        if end == None:
            end = datetime.datetime.utcnow()
        
        try:
            fun = self.evals[stat]
        except KeyError:
            logs.debug('Invalid or unsupported statistic')
        
        t0 = bgn
        output = []
        
        if scope == 'total':
            total = fun(bgn, end)
            output.append((bgn, end, total))
            
            if perUser:
                output = self.perUser(output)
            return output
        
        elif scope == 'day': 
            t1 = bgn + timedelta(days=1)
            
        elif scope == 'week': 
            t1 = bgn + datetime.timedelta(days=(7 - bgn.weekday()))
            
        elif scope == 'month': 
            t1 = incrMonth(bgn)
        
        while t0 < end:
            
            total = fun(t0, t1)
            
            output.append((t0, t1, total))
        
            t0 = t1
            if scope == 'day':
                t1 += timedelta(days=1)
            elif scope == 'week':
                t1 += timedelta(days=7)
            elif scope == 'month':
                t1 = incrMonth(t1)
            
            t1 = min(end, t1)
        
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
        return bgns, ends, values, base
    
        
        