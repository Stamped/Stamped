#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals

import calendar, datetime, sys, math
import keys.aws, logs, utils


from servers.analytics.core.Convert             import Converter
from boto.sdb.connection                        import SDBConnection
from boto.exception                             import SDBResponseError
from gevent.pool                                import Pool

#Score a user's week by involvement 




class weeklyScore(object):
    
    def __init__(self,api):
        self.api = api
        self.conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
        self.domains = {}
        self.statDict = {}

        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            self.domains[suffix] = self.conn.get_domain('bowser_%s' % (suffix))
    
    
    
    def scoreQuery(self,domain,t0,t1,uri,points):
        
        query = 'select uri,uid from `%s` where uri = "%s" and bgn >= "%s" and bgn <= "%s"' % (domain.name,uri,t0.isoformat(),t1.isoformat())
        stats = domain.select(query)
        
        for stat in stats:
            
            if 'uid' not in stat or 'uri' not in stat or 'cde' in stat:
                continue
            key = stat['uid']
            try:
                self.statDict[key] += points
            except KeyError:
                self.statDict[key] = points

    
    def segmentationReport(self,t0,t1,bMonth,percentage=False):
        self.statDict = {}
        
        scores = {
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
        
        pool = Pool(30)
        
        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            for uri in scores:
                pool.spawn(self.scoreQuery,self.domains[suffix],t0,t1,uri,scores[uri])
            
        pool.join()
        
        power = 0
        active = 0
        irregular = 0
        dormant = 0
        
        agg_score = 0
        
        if bMonth:
            POWER = 100
            AVERAGE = 10
        else: #Looking at a week
            POWER = 25
            AVERAGE = 5
            
        for uid in self.statDict:
            agg_score += self.statDict[uid]
            
            if self.statDict[uid] >= POWER:
                power += 1
            elif self.statDict[uid] >= AVERAGE:
                active += 1
            elif self.statDict[uid] > 0:
                irregular += 1
            else:
                dormant +=1

           
        users = len(self.statDict)
        
        if users == 0:
            return 0,0,0,0,0,0
        
        if percentage:
            power = float(power)/users*100
            active = float(active) / users*100
            irregular = float(irregular)/users*100
            dormant = float(dormant)/users*100

        mean_score = float(agg_score) / users
               
        
        return users,power,active,irregular,dormant,mean_score
        
        
        
        