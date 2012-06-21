#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals

import calendar, pprint, datetime, sys, argparse
import keys.aws, logs, utils
import Queries

from MongoStampedAPI                            import MongoStampedAPI
from boto.sdb.connection                        import SDBConnection
from boto.exception                             import SDBResponseError
from gevent.pool                                import Pool

class logsQuery(object):
    
    def __init__(self):
        self.conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
        self.domains = {}
        self.statSet  = set()
        self.statList = []

        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            self.domains[suffix] = self.conn.get_domain('stats_dev_%s' % (suffix))
            
            

    def performQuery(self,domain,fields,uri,t0,t1,unique):
        
        if uri is not None:
            query = 'select %s from `%s` where uri = "%s" and bgn >= "%s" and bgn <= "%s"' % (fields, domain.name, uri, t0.isoformat(), t1.isoformat())
        else:
            query = 'select %s from `%s` where bgn >= "%s" and bgn <= "%s"' % (fields, domain.name, t0.isoformat(), t1.isoformat())

        stats = domain.select(query)
        
        for stat in stats:
            try:
                if unique:
                    self.statSet.add(stat[fields])
                else:
                    self.statList.append(stat)
            except:
                pass
        
    def activeUsers(self,t0, t1):
        self.statSet = set()
        
        pool = Pool(16)
        
        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            #Just use collections inbox for speed
            #pool.spawn(self.performQuery,self.domains[suffix],'uid',"/v0/collections/inbox.json",t0,t1,True)
            
            #Use every api hit for accuracy
            pool.spawn(self.performQuery,self.domains[suffix],'uid',None,t0,t1,True)
        
        pool.join()
        
        return len(self.statSet)
    
    def newFriendships(self,t0,t1):
        self.statList = []
        
        pool = Pool(16)
        
        for i in range (0,16):
            suffix = '0'+hex(i)[2]
            pool.spawn(self.performQuery,self.domains[suffix],'*',"/v0/friendships/create.json",t0,t1,False)
        
        pool.join()
        
        return len(self.statList)
        
        
        
        
        
        
        