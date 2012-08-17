#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals

import logs, ast, time

from utils                                      import lazyProperty
from servers.analytics.core.AnalyticsUtils      import est, estMidnight
from servers.analytics.core.logsQuery           import logsQuery
from servers.analytics.core.SimpleDBConnection  import SimpleDBCacheConnection
from datetime                                   import timedelta

class LatencyReport(object):
    
    def __init__(self,logsQuery=logsQuery()):
        self.logsQ = logsQuery
    
    @lazyProperty
    def _cache(self):
        return SimpleDBCacheConnection('latency')
    
    # Get the overall api latency report for today
    def getTodaysLatency(self): 
        
        overall_stats = {}
        
        # Build up until the current hour (e.g. if it is currently 8:04, fill in stats thru 9:00)
        for hour in range (1, est().hour+1):
            stats = {}
            
            t0 = time.time()
            key = "hour-%s-%s" % (hour, estMidnight().date().isoformat())
            
            # See if we've stored hourly data earlier
            cached = self._cache.lookup(key)
            if cached is not None:
                for key, value in cached.items():
                    stats[str(key)] = ast.literal_eval(value)
                
                t1 = time.time()
                logs.debug("Cache hit for hour %s. Extraction time: %s seconds" % (hour, t1 - t0))
            
            # If not then pull the data from simpleDB (include scope distinction)
            else:
                stats = self.logsQ.latencyReport(estMidnight() + timedelta(hours=hour - 1),estMidnight() + timedelta(hours=hour), include_scope=True)
                
                t1 = time.time()
                logs.debug("Cache miss for hour %s. Extraction time: %s seconds" % (hour, t1 - t0))
                
                self._cache.store(key, stats)    
                
            # Aggregate hourly data into an overall representation
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
                    
                    # Standard deviation is the square root of variance
                    standard_dev = compound_variance ** 0.5
                    
                    # Ninetieth percentile has a z-score of 1.28. We are assuming that all stat samples are normally distributed 
                    # (which is a bold assumption to make but is the only way to get a close guess at 90th percentile)
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
    
    # Get the daily breakdown of latency statistics for a particular uri over a given time interval
    def dailyLatencySplits(self, uri, t0, t1, blacklist=[], whitelist=[]):
        report = {}
        
        # Get the appropriate EST start time from a UTC date
        start = estMidnight(t0 + timedelta(days=1))
        
        # Should run until the end of the date specified
        while start <= estMidnight(t1 + timedelta(days=1)):
            end = start + timedelta(days=1)
            report[start.date().isoformat()] = self.logsQ.latencyReport(start, end, uri, blacklist, whitelist)
            start += timedelta(days=1)
            
        return report
            
    
    
    

        
        
    
    

