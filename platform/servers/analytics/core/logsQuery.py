#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals

import keys.aws, logs, time

from datetime                                   import timedelta
from utils                                      import lazyProperty
from servers.analytics.core.SimpleDBConnection  import SimpleDBConnection, SimpleDBCacheConnection
from servers.analytics.core.AnalyticsUtils      import v1_init, v2_init, now, percentile, estMidnight

# Class containing the most useful and common queries to simpledb
# This module is independent of the stack from which it is run
class logsQuery(object):
    
    def __init__(self, domain_name='bowser'):   
        self.conn = SimpleDBConnection(domain_name)
        
        
    @lazyProperty
    def _customCache(self):
        return SimpleDBCacheConnection('custom')    
    
    # Number of active users in a given time period
    # Counts the number of users in the time window that have triggered an unread activity api call indicating their usage of the app
    # Optionally can return a list of users instead of a count (last kwarg)
    def activeUsers(self, bgn, end, list=False):

        users = self.conn.queryForUserSet(params=['uri="/v1/activity/unread.json"'], bgn=bgn, end=end)
        
        if list:
            return users
        else:
            return len(users)
    
    # Number of users who opened the guide (or a particular section of the guide) within the given time window
    def guideUsers(self, bgn, end, section=None, list=False):
        
        params = ['uri="/v1/guide/collection.json"']
        
        if section is not None:
            params.append('frm_section="%s"' % section)

        users = self.conn.queryForUserSet(params=params, bgn=bgn, end=end)
        
        if list:
            return users
        else:
            return len(users)
    
    # Number of users who viewed universal news in the given time window
    def universalNewsUsers(self, bgn, end, list=False):

        users = self.conn.queryForUserSet(params=['uri="/v1/activity/collection.json"', 'frm_scope="friends"'], bgn=bgn, end=end)
        
        if list:
            return users
        else:
            return len(users)
    
    # Number of users who took an action on an entity in the given time window
    def entityActionUsers(self, bgn, end, source=None, action=None, list=False):
        
        params = ['uri="/v1/actions/complete.json"']
        
        if source is not None:
            params.append('frm_source="%s"' % source)
            
        if action is not None:
            params.append('frm_action="%s"' % action)

        users = self.conn.queryForUserSet(params=params, bgn=bgn, end=end)

        if list:
            return users
        else:
            return len(users)
    
    # Check the number of users who followed somebody within n days of launch and returned to follow another user later on
    def launchDayFollowRetention(self, version="v2", days=2):
        
        if version == "v2":
            bgn = v2_init()
            end = now()
        else:
            bgn = v1_init()
            end = v2_init()
            
        cutoff = bgn + timedelta(days=days)
        
        launch_followers = self.conn.queryForUserSet(params=['uri="/v1/friendships/create.json"'], bgn=bgn, end=cutoff)
        new_followers = self.conn.queryForUserSet(params=['uri="/v1/friendships/create.json"'], bgn=cutoff, end=end)
        
        returning_followers = set.intersection(launch_followers,new_followers)
        rate = float(len(returning_followers)) / len(launch_followers)
        
        print "Users adding freinds in first %s days: %s" % (days, len(launch_followers))
        print "Users adding friends again more recently: %s" % len(returning_followers)
        print "Retention Rate: %.3f%%" % (rate * 100)
        
        return len(launch_followers), len(returning_followers), rate
    
    # Number of users who opened the guide once and came back to open it again a different day
    def guideReturnRate(self):
        
        previous_users = set()
        returning_users = set()
        bgn = v2_init()
        end = v2_init() + timedelta(days=1)
        
        while end < now():
            days_users = self.conn.queryForUserSet(params=['uri="/v1/guide/collection.json"'], bgn=bgn, end=end)
            returning_users.update(set.intersection(previous_users, days_users))
            previous_users.update(days_users)
            
            bgn += timedelta(days=1)
            end += timedelta(days=1)
        
        rate = float(len(returning_users)) / len(previous_users)
        
        print "Number of guide users: %s" % len(previous_users)
        print "Number of returning guide users %s" % len(returning_users)
        print "Retention rate: %.3f%%" % (rate * 100)

    # Latency analysis for all or a single uri
    def latencyReport(self, bgn, end, uri=None, blacklist=[], whitelist=[], include_scope=True):
        statDict = {}
        errDict = {}
        
        # Build the query 
        params = []
        if uri is not None:
            params.append('uri="%s"' % uri)
        else:
            params.append('uri like "/v1/%"')
        
        if len(whitelist) > 0:
            # Convert whitelist into a string representation of a tuple sans trailing comma
            w = str(tuple(whitelist)).replace(',)',')')
            params.append('uid in %s' % w)
        else:
            for blacklistedId in blacklist:
                params.append('uid != "%s"' % blacklistedId)
        
        data = self.conn.query(params=params, bgn=bgn, end=end, fields=['uri','dur','frm_scope','cde'])
        
        # Convert the results into a dictionary with different uris as keys
        for stat in data:
            if 'dur' not in stat:
                continue
            else:
                diff = stat['dur'] / 1000000.0
                key = stat['uri']

                if 'frm_scope' in stat and include_scope:
                    key += "?scope=%s" % stat['frm_scope']
                
                if 'cde' in stat:
                    errType = stat['cde'][0]
                    if errType != "4" and errType != "5":
                        continue
                    try:
                        errDict['%s-%s' % (key,errType)] += 1
                    except KeyError:
                        errDict['%s-%s' % (key,errType)] = 1
                else:
                    try:
                        statDict[key].append(diff)
                    except KeyError:
                        statDict[key] = [diff]
        
        # Iterate through the dictionary of uris and diffs to calculate stats that we care about
        output = {}
        for uri, diffs in statDict.items():
            agg = sum(diffs)
            n = len(diffs)
            mean = float(agg) / n
            sortedDiffs = sorted(diffs)
            max = sortedDiffs[-1]
            median = percentile(sortedDiffs, .5)
            ninetieth = percentile(sortedDiffs, .9)
            
            inner_sum = reduce(lambda agg,i: agg + (i - mean) ** 2, diffs, 0)
            variance = (1.0 / n) * inner_sum
            
            errors4 = 0
            errors5 = 0
            if uri+'-4' in errDict:
                errors4 = errDict[uri+'-4']
            if uri+'-5' in errDict:
                errors5 = errDict[uri+'-5']
            
            output[uri] = {'mean' : mean,
                           'median' : median,
                           'ninetieth' : ninetieth,
                           'variance' : variance,
                           'length' : n,
                           'max': max,
                           '400_errors' : errors4,
                           '500_errors' : errors5
                           }
            
        return output

    # Interval-based report on the stress level of the Stamped prod stack
    def qpsReport(self, time, interval, total_seconds):        
        count_report = {}
        mean_report = {}
        
        base_time = time - timedelta(seconds=total_seconds)
        for i in range(total_seconds/interval):
            statCountByNode = {}
            statTimeByNode = {}
            
            bgn = base_time + timedelta(seconds=i*interval)
            end = base_time + timedelta(seconds=(i+1)*interval)
            
            data = self.conn.query(bgn=bgn, end=end, fields=['nde','dur'])
            
            for stat in data:
                if 'dur' not in stat or 'nde' not in stat:
                    continue
                else:
                    diff = stat['dur'] / 1000000.0
                    try:
                        statCountByNode[stat['nde']] += 1
                        statTimeByNode[stat['nde']] += diff
                    except KeyError:
                        statCountByNode[stat['nde']] = 1
                        statTimeByNode[stat['nde']] = diff

            for node, count in statCountByNode.items():
                mean = float(statTimeByNode[node]) / count
                try:
                    # Pad with zeros until the current position
                    while len(count_report[node]) < i:
                        count_report[node].insert(0,0)
                        mean_report[node].insert(0,0)
                    count_report[node].insert(0,"%.3f" % (float(count) / interval))
                    mean_report[node].insert(0,"%.3f" % (mean))
                except KeyError:
                    count_report[node] = [0]*i
                    mean_report[node] = [0]*i
                    count_report[node].insert(0,"%.3f" % (float(count) / interval))
                    mean_report[node].insert(0,"%.3f" % (mean))
        
        # Pad with zeros to reach appropriate length            
        for node in count_report:
            while len(count_report[node]) < total_seconds/interval:
                count_report[node].insert(0,0)
                mean_report[node].insert(0,0)
        
        return count_report, mean_report
    
    # Used for looking up custom stats and checking for cached values
    def customQuery(self, stat_name, params, bgn, end):
        
        key = "%s-%s" % (stat_name, bgn.date().isoformat())
        
        cached = None
        # Only lookup from the cache for a daily number (haven't set up for storing months or weeks yet
        if end - bgn == timedelta(days=1):
            cached = self._customCache.lookup(key)
        
        if cached is not None:
            return int(cached['data'])
        
        elif stat_name == 'users':
            data = self.activeUsers(bgn, end)
        else: 
            data = self.conn.count(params=params, bgn=bgn, end=end)
        
        if bgn.date() < estMidnight().date():
            cache_dict = {'data' : data}
            self._customCache.store(key, cache_dict)
        
        return data
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        