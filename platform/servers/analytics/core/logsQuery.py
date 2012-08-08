#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals

import calendar, pprint, datetime, sys, math
import keys.aws, logs, utils

from api.MongoStampedAPI                        import MongoStampedAPI
from boto.sdb.connection                        import SDBConnection
from boto.exception                             import SDBResponseError
from gevent.pool                                import Pool
from analytics_utils                            import today, v2_init,now



def percentile(numList,p):
    #Assumes numList is sorted
    k = (len(numList)-1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return numList[int(k)]
    d0 = numList[int(f)] * (c-k)
    d1 = numList[int(c)] * (k-f)
    return d0+d1
    

class logsQuery(object):
    
    def __init__(self,domain_name=None):
        self.conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
        self.domains = {}
        self.statSet  = set()
        self.statDict = {}
        self.errDict = {}
        self.statCount = 0
        self.statCountByNode = {}
        self.statTimeByNode = {}

        if domain_name is None:
            domain_name = 'bowser'
            
        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            self.domains[suffix] = self.conn.get_domain('%s_%s' % (domain_name,suffix))
            
            

    def performQuery(self,domain,fields,uri,t0,t1,byNode=False,form_dict={},logged_out=False):
        
        if uri is not None:
            query = 'select %s from `%s` where uri = "%s" and bgn >= "%s" and bgn <= "%s"' % (fields, domain.name, uri, t0.isoformat(), t1.isoformat())
        else:
            query = 'select %s from `%s` where bgn >= "%s" and bgn <= "%s"' % (fields, domain.name, t0.isoformat(), t1.isoformat())

        
        for key, value in form_dict.items():
            query = '%s and frm_%s = "%s"' % (query, key, value)
            
        stats = domain.select(query)
        
        for stat in stats:
            
            if fields == 'count(*)':
                self.statCount += int(stat['Count'])
            elif byNode:
                bgn = stat['bgn'].split('T')
                end = stat['end'].split('T')
                if end[0] == bgn[0]:
                    bgn = bgn[1].split(':')
                    end = end[1].split(':')
                    hours = float(end[0]) - float(bgn[0])
                    minutes = float(end[1]) - float(bgn[1])
                    seconds = float(end[2]) - float(bgn[2])
                    diff = seconds + 60*(minutes + 60*hours)
                
                try:
                    self.statCountByNode[stat['nde']] += 1
                    self.statTimeByNode[stat['nde']] += diff
                except KeyError:
                    self.statCountByNode[stat['nde']] = 1
                    self.statTimeByNode[stat['nde']] = diff
            elif logged_out and 'uid' not in stat:
                self.statCount += 1
                print stat
            else:
                try:
                    self.statSet.add(stat[fields])
                except KeyError:
                    pass
        
        
    def activeUsers(self,t0, t1):
        self.statSet = set()
        
        pool = Pool(16)
        
        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            #Just use collections inbox for speed
            pool.spawn(self.performQuery,self.domains[suffix],'uid',"/v1/activity/unread.json",t0,t1)
        
        pool.join()
        
        return len(self.statSet)
    
    # Guide Users
    def guideReport(self, t0, t1, section=None):
        self.statSet = set()
        self.statCount = 0
        
        pool = Pool(16)
        
        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            if section is not None:
                pool.spawn(self.performQuery,self.domains[suffix],'count(*)',"/v1/guide/collection.json",t0,t1, form_dict={'section': section})
            else:
                pool.spawn(self.performQuery,self.domains[suffix],'uid',"/v1/guide/collection.json",t0,t1)
        
        pool.join()
        
        return self.statCount
    
    # Universal news users
    def newsUsers(self, t0, t1):
        self.statSet = set()
        
        pool = Pool(16)
        
        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            pool.spawn(self.performQuery, self.domains[suffix], 'uid', "/v1/activity/collection.json", t0, t1, form_dict={'scope': 'friends'})
        
        pool.join()
        
        return len(self.statSet)
    
    def entityActionUsers(self, t0, t1, source=None, action=None):
        self.statSet = set()
        
        form = {}
        
        if source is not None:
            form['source'] = source
        
        if action is not None:
            form['action'] = action
            
        pool = Pool(16)
        
        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            pool.spawn(self.performQuery, self.domains[suffix], 'uid', "/v1/actions/complete.json", t0, t1, form_dict=form)
        
        pool.join()
        
        return len(self.statSet)

    
    
    def latencyQuery(self,domain,t0,t1,uri,blacklist,whitelist):
        if uri is None:
            query = 'select uri,frm_scope,bgn,end,cde,uid from `%s` where uri like "/v1/%%" and bgn >= "%s" and bgn <= "%s"' % (domain.name,t0.isoformat(),t1.isoformat())
        else:
            query = 'select uri,frm_scope,bgn,end,cde,uid from `%s` where uri = "%s" and bgn >= "%s" and bgn <= "%s"' % (domain.name,uri,t0.isoformat(),t1.isoformat())
        stats = domain.select(query)
        
        for stat in stats:
            if 'uid' in stat and stat['uid'] in blacklist:
                continue
            elif len(blacklist) == 0 and len(whitelist) > 0 and 'uid' in stat and stat['uid'] not in whitelist:
                continue
            bgn = stat['bgn'].split('T')
            end = stat['end'].split('T')
            if end[0] == bgn[0]:
                bgn = bgn[1].split(':')
                end = end[1].split(':')
                hours = float(end[0]) - float(bgn[0])
                minutes = float(end[1]) - float(bgn[1])
                seconds = float(end[2]) - float(bgn[2])
                diff = seconds + 60*(minutes + 60*hours)
                key = stat['uri']

                if 'frm_scope' in stat:
                    key = "%s?scope=%s" % (stat['uri'], stat['frm_scope'])
                
                if 'cde' in stat:
                    errType = stat['cde'][0]
                    if errType != "4" and errType != "5":
                        print stat
                        continue
                    try:
                        self.errDict['%s-%s' % (key,errType)] += 1
                    except KeyError:
                        self.errDict['%s-%s' % (key,errType)] = 1
                else:
                    try:
                        self.statDict[key].append(diff)
                    except KeyError:
                        self.statDict[key] = [diff]


    def latencyReport(self,t0,t1,uri=None,blacklist=[],whitelist=[]):
        self.statDict = {}
        self.errDict = {}
        
        pool = Pool(16)
        
        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            pool.spawn(self.latencyQuery,self.domains[suffix],t0,t1,uri,blacklist,whitelist)
            
        pool.join()
        
        output = {}
        
        for uri, diffs in self.statDict.items():
            agg = sum(diffs)
            n = len(diffs)
            mean = float(agg) / n
            sortedDiffs = sorted(diffs)
            max = sortedDiffs[-1]
            median = percentile(sortedDiffs, .5)
            ninetieth = percentile(sortedDiffs, .9)
            
            inner_sum = reduce(lambda agg,i: agg + (i - mean) ** 2, diffs, 0)
            variance = ((1.0 / n) * inner_sum) ** 0.5
            
            errors4 = 0
            errors5 = 0
            if uri+'-4' in self.errDict:
                errors4 = self.errDict[uri+'-4']
            if uri+'-5' in self.errDict:
                errors5 = self.errDict[uri+'-5']
            
            output[uri] = {'mean' : mean,
                           'median' : median,
                           'ninetieth' : ninetieth,
                           'variance' : variance,
                           'length' : n,
                           '400 errors' : errors4,
                           '500 errors' : errors5
                           }
            
        return output
              
    def qpsReport(self,time,interval,total_seconds):
        blacklist=[]
        whitelist=[]
        

        count_report = {}
        mean_report = {}
        t0 = time - datetime.timedelta(0,total_seconds)
        for i in range (0,total_seconds/interval):
            self.statCountByNode = {}
            self.statTimeByNode = {}
            
            t1 = t0 + datetime.timedelta(0,i*interval)
            t2 = t0 + datetime.timedelta(0,(i+1)*interval)
            
            pool = Pool(32)
        
            for j in range (0,16):
                suffix = '0'+hex(j)[2]
                
                pool.spawn(self.performQuery,self.domains[suffix],'nde,bgn,end',None,t1,t2,byNode=True)
    
            pool.join()
            

            for node in self.statCountByNode:
                count = self.statCountByNode[node]
                mean = float(self.statTimeByNode[node])/count
                try:
                    while len(count_report[node]) < i:
                        count_report[node].insert(0,0)
                        mean_report[node].insert(0,0)
                    count_report[node].insert(0,"%.3f" % (float(count)/interval))
                    mean_report[node].insert(0,"%.3f" % (mean))
                except KeyError:
                    count_report[node] = [0]*i
                    mean_report[node] = [0]*i
                    count_report[node].insert(0,"%.3f" % (float(count)/interval))
                    mean_report[node].insert(0,"%.3f" % (mean))
                    
        for node in count_report:
            while len(count_report[node]) < total_seconds/interval:
                count_report[node].insert(0,0)
                mean_report[node].insert(0,0)
        
        return count_report,mean_report
        
    def customQuery(self,t0,t1,fields,uri,form={},logged_out=False):
        
        if fields == 'count(*)':
            self.statCount = 0
        else:
            self.statSet = set()
        
        pool = Pool(16)
        
        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            
            pool.spawn(self.performQuery,self.domains[suffix],fields,uri,t0,t1,form_dict=form,logged_out=logged_out)

        pool.join()
        
        if fields == 'count(*)':
            return self.statCount
        else:
            return len(self.statSet)

        
        
        
        