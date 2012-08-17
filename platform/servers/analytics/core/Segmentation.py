#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals

import logs, utils


from servers.analytics.core.logsQuery import logsQuery

# Score a user's week/month by involvement 
class SegmentationReport(object):
    
    def __init__(self, logsQuery=logsQuery()):
        self.logsQ = logsQuery
    
        self.scores = {
            #2 points for likes
            '/v1/stamps/likes/create.json': 2,
            '/v1/stamps/likes/remove.json': -2,
            
            #2 points for todos
            '/v1/todos/create.json': 2,
            '/v1/todos/remove.json': -2,
            
            #3 points for comments
            '/v1/comments/create.json': 3,
            '/v1/comments/remove.json': -3,
            
            #3 points for adding a friend
            '/v1/friendships/create.json': 3,
            '/v1/friendships/remove.json': -3,
            
            #3 points for taking an action
            '/v1/actions/complete.json': 2,
            
            #5 points for a stamp
            '/v1/stamps/create.json': 5,
            '/v1/stamps/remove.json': -5,
            
            #5 points for an invite
            '/v1/frienships/invite.json': 5,
            
            }
    
    def getUserPointTotals(self, bgn, end):
        
        userStats = {}
        
        for uri in self.scores:

            data = self.logsQ.conn.query(params=['uri="%s"' % uri], bgn=bgn, end=end, fields=['uid'])
            for item in data:
                if 'uid' in item:
                    user_id = item['uid']
                    try:
                        userStats[user_id] += self.scores[uri]
                    except KeyError:
                        userStats[user_id] = self.scores[uri]
        
        return userStats
    
    def weeklySegmentationReport(self, bgn, end, percentage=False, monthly=False):
        
        userStats = self.getUserPointTotals(bgn, end)
        
        power_users = 0
        active_users = 0
        irregular_users = 0
        dormant_users = 0
        agg_score = 0
        
        if monthly:
            POWER = 100
            AVERAGE = 10
        else:
            POWER = 25
            AVERAGE = 5
            
        for uid, score in userStats.items():
            
            agg_score += score
            
            if score >= POWER:
                power_users += 1
            elif score >= AVERAGE:
                active_users += 1
            elif score > 0:
                irregular_users += 1
            else:
                dormant_users +=1

           
        total_users = len(userStats)
        
        if total_users == 0:
            return 0, 0, 0, 0, 0, 0
        
        if percentage:
            power_users = float(power_users) / total_users * 100
            active_users = float(active_users) / total_users * 100
            irregular_users = float(irregular_users) / total_users * 100
            dormant_users = float(dormant_users) / total_users * 100

        mean_score = float(agg_score) / total_users
               
        
        return total_users, power_users, active_users, irregular_users, dormant_users, mean_score
        
        
        
        