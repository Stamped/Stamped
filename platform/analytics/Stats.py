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

from MongoStampedAPI                    import MongoStampedAPI
from boto.sdb.connection                import SDBConnection
from boto.exception                     import SDBResponseError
from db.mongodb.MongoStatsCollection    import MongoStatsCollection
from gevent.pool                        import Pool
from logsQuery                          import logsQuery
 
#Handle command line input

parser = argparse.ArgumentParser(description='Queries for vital statistics over a selected timeframe. Default is total')
parser.add_argument('vital', help="The statistic you are querying for: ", nargs=1)
parser.add_argument('bgn', help='Begin date for stats, format: yyyy-mm-dd', nargs=1)
parser.add_argument('end', help='End date for stats, format: yyyy-mm-dd (optional - default is same as bgn)', nargs='?', default='bgn')
parser.add_argument('-d', help='Show daily totals between bgn and end', action='store_true')
parser.add_argument('-w', help='Show weekly totals between bgn and end', action='store_true')
parser.add_argument('-m', help='Show monthly totals between bgn and end', action='store_true')
parser.add_argument('--prod', help='Ignore data past the most recent data copy from prod to dev', action='store_true')
parser.add_argument('-perUser', help='Show stats on a per active user basis', action='store_true')


args = parser.parse_args()
d, w, m, vital, bgn, end, prod, per = [args.d, args.w, args.m, args.vital[0], args.bgn[0], args.end, args.prod, args.perUser]


#Get all of our dates correctly formatted

_day = datetime.timedelta(hours=23, minutes=59, seconds=59,microseconds=999999)

try:
    bgn = bgn.split('-')
    bgn = datetime.datetime(int(bgn[0]),int(bgn[1]),int(bgn[2]))
except:
    print "Bad value for bgn. Please format according to yyyy-mm-dd"
    sys.exit()

if end == 'bgn':
    end = bgn + _day

else:
    try:
        end = end.split('-')
        end = datetime.datetime(int(end[0]),int(end[1]),int(end[2]),23,59,59,999999)
    except:
        print "Bad value for end. Please format according to yyyy-mm-dd"
        sys.exit()
        
if prod and (end > datetime.datetime (2012,6,4,19,12)):
    end = datetime.datetime (2012,6,4,19,12)
    
    
if vital != 'stamps' and vital != 'accounts' and vital != 'users' and vital != 'friendships':
    print "Bad value for vital. Please enter either 'stamps', 'accounts', 'friendships' or 'users'"
    sys.exit()


#Functions for computing stats
api = MongoStampedAPI()
logsQ = logsQuery()


def incrMonth(date):
    succ = date.month
    year = date.year + succ / 12
    succ = succ % 12 + 1
    day = min(date.day,calendar.monthrange(year,succ)[1])
    return datetime.datetime(year,succ,day)
    
evals = {
         'stamps': Queries.newStamps,
         'accounts': Queries.newAccounts,
         'friendships': (lambda t0, t1: logsQuery.newFriendships(logsQ,t0,t1)),
         'users': (lambda t0, t1: logsQuery.activeUsers(logsQ,t0,t1))}

def compute():
    
    prev = bgn
    agg=0
    output = []
    printing = []
    
    #No flags
    if not (d or w or m):
        try:
            fun = evals[vital] 
            total = fun(bgn, end)
        except Exception:
            raise
        output.append((bgn,end,total))
        return output
    
    
    if d: 
        interval = int((end.date() - bgn.date()).total_seconds()/(60*60*24)+1)
        succ = bgn + _day
        
    elif w: 
        interval = int((end.date() - bgn.date()).total_seconds()/(60*60*24*7)+1)
        succ = bgn + datetime.timedelta(days= (6-bgn.weekday())) + _day
        
    elif m: 
        interval = ((end.year-bgn.year)*12 + end.month) - bgn.month +1
        days_left = calendar.monthrange(bgn.year, bgn.month)[1] - bgn.day
        succ = bgn + datetime.timedelta(days=days_left) + _day
    
    for i in range (1,interval+1):
        
        if prev != bgn:
            if d:
                succ = prev + _day
            elif w:
                succ = prev + datetime.timedelta(days=6) + _day
            elif m:
                succ = incrMonth(prev) + datetime.timedelta(microseconds=-1)
        
        if succ > end:
            succ = end
        
        try:
            fun = evals[vital] 
            total = fun(prev, succ)
        except Exception:
            raise
        
        
        output.append((prev,succ,total))
        prev = succ + datetime.timedelta(microseconds=1)
        agg += total
    
    output.append((bgn,end,agg))
    return output



def perUser(computed):
    out = []
    #totalUsers = 0
    for i in range (0,len(computed)-1):
        computed
        t0,t1 = computed[i][0], computed[i][1]
        users = evals['users'](t0,t1)
        if users == 0:
            out.append((t0.isoformat(),t1.isoformat(),'No Users'))
        else:
            out.append((t0.isoformat(),t1.isoformat(),float(computed[i][2])/users))
        #totalUsers += users
    #out.append(('average',float(computed[len(computed)-1][1])/totalUsers))
    return out




if not per:
    result = compute()
    for out in result:
        print "%s - %s\t%s" % (out[0],out[1],out[2])
else:
    result = perUser(compute())
    for out in result:
        print "%s - %s\t%s" % (out[0],out[1],out[2])




