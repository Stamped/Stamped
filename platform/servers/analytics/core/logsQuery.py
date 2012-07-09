#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals

import calendar, pprint, datetime, sys, math
import keys.aws, logs, utils

from api.MongoStampedAPI                            import MongoStampedAPI
from boto.sdb.connection                        import SDBConnection
from boto.exception                             import SDBResponseError
from gevent.pool                                import Pool


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
    
    def __init__(self):
        self.conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
        self.domains = {}
        self.statSet  = set()
        self.statDict = {}
        self.errDict = {}
        self.statCount = 0

        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            self.domains[suffix] = self.conn.get_domain('stats_dev_%s' % (suffix))
            
            

    def performQuery(self,domain,fields,uri,t0,t1):
        
        if uri is not None:
            query = 'select %s from `%s` where uri = "%s" and bgn >= "%s" and bgn <= "%s"' % (fields, domain.name, uri, t0.isoformat(), t1.isoformat())
        else:
            query = 'select %s from `%s` where bgn >= "%s" and bgn <= "%s"' % (fields, domain.name, t0.isoformat(), t1.isoformat())

        stats = domain.select(query)
        
        for stat in stats:
            try:
                if fields == 'count(*)':
                    self.statCount += int(stat['Count'])
                else:
                    self.statSet.add(stat[fields])
            except KeyError:
                pass
        
    def activeUsers(self,t0, t1):
        self.statSet = set()
        
        pool = Pool(16)
        
        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            #Just use collections inbox for speed
            pool.spawn(self.performQuery,self.domains[suffix],'uid',"/v0/activity/unread.json",t0,t1)
        
        pool.join()
        
        return len(self.statSet)
    
    def latencyQuery(self,domain,t0,t1,uri,blacklist,whitelist):
        if uri is None:
            query = 'select uri,frm_scope,bgn,end,cde,uid from `%s` where uri like "/v0%%" and bgn >= "%s" and bgn <= "%s"' % (domain.name,t0.isoformat(),t1.isoformat())
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
                    try:
                        self.errDict['%s-%s' % (key,errType)] +=1
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
        
        for uri in self.statDict:
            sum = 0
            max = 0
            for num in self.statDict[uri]:
                sum += num
                if num > max:
                    max = num
            mean = float(sum) / len(self.statDict[uri])
            sorte = sorted(self.statDict[uri])
            median = percentile(sorte,.5)
            ninetieth = percentile(sorte,.9)
            n = len(self.statDict[uri])
            errors4 = 0
            errors5 = 0
            if uri+'-4' in self.errDict:
                errors4 = self.errDict[uri+'-4']
            if uri+'-5' in self.errDict:
                errors5 = self.errDict[uri+'-5']
            
            self.statDict[uri] = '%.3f' % mean,'%.3f' % median,'%.3f' % ninetieth, '%.3f' % max, n, errors4,errors5
            
        return self.statDict
    
    
    def dailyLatencyReport(self,t0,t1,uri,blacklist,whitelist):
        self.statDict = {}
        diff = (t1 - t0).days
        output = []
        for i in range (0,diff):
            t2 = t0+datetime.timedelta(days=i)
            t3 = t0+datetime.timedelta(days=i+1)
            self.statDict = {}
            self.errDict = {}
            
            pool = Pool(16)
            
            for k in range (0,16):
                suffix = '0'+hex(k)[2]
                pool.spawn(self.latencyQuery,self.domains[suffix],t2,t3,uri,blacklist,whitelist)
                
            pool.join()
            
            for uri in self.statDict:
                sum = 0
                max = 0
                for num in self.statDict[uri]:
                    sum += num
                    if num > max:
                        max = num
                mean = float(sum) / len(self.statDict[uri])
                sorte = sorted(self.statDict[uri])
                median = percentile(sorte,.5)
                ninetieth = percentile(sorte,.9)
                n = len(self.statDict[uri])
                errors4 = 0
                errors5 = 0
                if uri+'-4' in self.errDict:
                    errors4 = self.errDict[uri+'-4']
                if uri+'-5' in self.errDict:
                    errors5 = self.errDict[uri+'-5']
                
                output.append((t2.date().isoformat(),'%.3f' % mean,'%.3f' % median,'%.3f' % ninetieth, '%.3f' % max, n, errors4,errors5))
                
        return output
        
    def customQuery(self,t0,t1,fields,uri):
        
        if fields == 'count(*)':
            self.statCount = 0
        else:
            self.statSet = set()
        
        pool = Pool(16)
        
        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            
            pool.spawn(self.performQuery,self.domains[suffix],fields,uri,t0,t1)

        pool.join()
        
        if fields == 'count(*)':
            return self.statCount
        else:
            return len(self.statSet)

        
        
        
        