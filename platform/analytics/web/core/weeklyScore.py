#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals

import calendar, datetime, sys, argparse,math
import keys.aws, logs, utils

from Convert import Converter
from MongoStampedAPI                            import MongoStampedAPI
from boto.sdb.connection                        import SDBConnection
from boto.exception                             import SDBResponseError
from gevent.pool                                import Pool

#Score a user's week by involvement 

def score(uri):
    scores = {
            #2 points for likes
            '/v0/stamps/likes/create.json': 2,
            '/v0/stamps/likes/remove.json': -2,
            
            #2 points for todos
            '/v0/todos/create.json': 2,
            '/v0/todos/remove.json': -2,
            
            #3 points for comments
            '/v0/comments/create.json': 3,
            '/v0/comments/remove.json': -3,
            
            #3 points for adding a friend
            '/v0/friendships/create.json': 3,
            '/v0/friendships/remove.json': -3,
            
            #3 points for taking an action
            '/v0/actions/complete.json': 2,
            
            #5 points for a stamp
            '/v0/stamps/create.json': 5,
            '/v0/stamps/remove.json': -5,
            
            #5 points for an invite
            '/v0/frienships/invite.json': 5,
            
              }
    if uri in scores:
        return scores[uri]
    else:
        return 0


class weeklyScore(object):
    
    def __init__(self,api):
        self.api = api
        self.conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
        self.domains = {}
        self.statDict = {}

        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            self.domains[suffix] = self.conn.get_domain('stats_dev_%s' % (suffix))
    
    
    
    def scoreQuery(self,domain,t0,t1):
        
        
        query = 'select uri,uid from `%s` where uri like "/v0%%" and bgn >= "%s" and bgn <= "%s"' % (domain.name,t0.isoformat(),t1.isoformat())
        stats = domain.select(query)
        
        for stat in stats:
            
            if 'uid' not in stat or 'uri' not in stat or 'cde' in stat:
                continue
            key = stat['uid']
            points = score(stat['uri'])
            if points is not 0:
                try:
                    self.statDict[key] += points
                except KeyError:
                    self.statDict[key] = points

    
    
    def calculateScores(self,t0,t1):
        self.statDict = {}
        
        pool = Pool(16)
        
        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            pool.spawn(self.scoreQuery,self.domains[suffix],t0,t1)
            
        pool.join()
        
        convert = Converter(self.api)
        output = []
        
        for uid in self.statDict:
            sname = convert.convert(uid)
            output.append((sname,self.statDict[uid]))
            
        return sorted(output, key= lambda x: x[1], reverse = True)
    
    def segmentationReport(self,t0,t1,bMonth):
        self.statDict = {}
        
        pool = Pool(16)
        
        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            pool.spawn(self.scoreQuery,self.domains[suffix],t0,t1)
            
        pool.join()
        
        power = 0
        avg = 0
        lurker = 0
        dormant = 0
        retractors = 0
        
        agg_score = 0
        
        if bMonth:
            Power = 100
            Average = 10
        else: #Looking at a week
            Power = 25
            Average = 5
            
        for uid in self.statDict:
            agg_score += self.statDict[uid]
            
            if self.statDict[uid] >= Power:
                power += 1
            elif self.statDict[uid] >= Average:
                avg += 1
            elif self.statDict[uid] > 0:
                lurker += 1
            elif self.statDict[uid] == 0:
                dormant +=1
            else: 
                retractors += 1
           
        users = len(self.statDict)
        power = float(power)/users*100
        avg = float(avg) / users*100
        lurker = float(lurker)/users*100
        dormant = float(dormant)/users*100
        retractors = float(retractors)/users*100
        mean_score = float(agg_score) / users
        
        return users,power,avg,lurker,dormant,mean_score
        
        
        
        