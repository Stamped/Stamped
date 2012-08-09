#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals

import keys.aws, logs, utils, math
import ast

from boto.sdb.connection                        import SDBConnection
from servers.analytics.core.analytics_utils     import *
from servers.analytics.core.logsQuery           import logsQuery
from servers.analytics.core.statWriter          import statWriter
from gevent.pool                                import Pool
from time                                       import time



class LatencyReport(object):
    
    def __init__(self,logsQuery=logsQuery()):
        self.logsQ = logsQuery
        self.writer = statWriter('latency',conn=self.logsQ.conn)
        self.cache = self.logsQ.conn.get_domain('latency')
    
    
    def getTodaysLatency(self): 
        
        overall_stats = {}
        
        # Build up until the current hour (e.g. if it is currently 8:04, fill in stats thru 9:00)
        for hour in range (1, est().hour+1):
            stats = {}
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

            for key,values in stats.items():
                if key not in overall_stats:
                    overall_stats[key] = values
                else:
                    overall = overall_stats[key]
                    
                    total_length = overall['length'] + values['length']
                    
                    compound_mean = ((overall['mean'] * overall['length']) + (values['mean'] * values['length'])) / total_length
                    
                    # This is a crappy and relatively inaccurate way to calculate aggregate median (just a weighted average of the medians)
                    compound_median = ((overall['median'] * overall['length']) + (values['median'] * values['length'])) / total_length
                    
                    # Calculate the compound variance 
                    compound_variance = (values['length'] * (values['variance'] + (compound_mean - values['mean'])**2) +
                                         overall['length'] * (overall['variance'] + (compound_mean - overall['mean'])**2)) / total_length
                    
                    # Standard deviation is teh square root of variance
                    standard_dev = compound_variance ** 0.5
                    
                    # Ninetieth percentile has a z-score of 1.28. We are assuming that all stat samples are normally distributed (which is a huge assumption to make but is the only way to get a close guess at 90th percentile)
                    ninetieth = compound_mean + (standard_dev * 1.28)
                    
                    overall['max'] = max(values['max'], overall['max'])
                    overall['median'] = compound_median
                    overall['mean'] = compound_mean
                    overall['variance'] = compound_variance
                    overall['length'] = total_length
                    overall['ninetieth'] = ninetieth
                    overall['500_errors'] += values['500_errors']
                    overall['400_errors'] += values['400_errors']
                
        return overall_stats
    
        
    def dailyLatencySplits(self,uri,t0,t1,blacklist,whitelist):
        report = {}
        start = today(t0)
        
        while start < today(t1):
            end = start + timedelta(days=1)
            report[start.date().isoformat()] = self.logsQ.latencyReport(start, end, uri, blacklist, whitelist)
            start += timedelta(days=1)
            
        return report
            
    
    
    

        
        
    
    

