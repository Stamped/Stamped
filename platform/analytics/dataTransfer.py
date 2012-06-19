import Globals
import sys
import keys.aws, logs, utils, time
import boto

from MongoStampedAPI                        import MongoStampedAPI
from db.mongodb.MongoStatsCollection        import MongoStatsCollection
from bson.objectid                          import ObjectId
from gevent.pool                            import Pool


conn = boto.connect_sdb("AKIAJPJJ2QXCMPIITWDQ","XwBv06/ezFEjsJvalbLNgE9IrHJ46DlGtWc5/F+X")
domain = conn.get_domain('stats-dev')

api = MongoStampedAPI()
sample = MongoStatsCollection()._collection.find()

to_add = {}

count = 0
failures = 0
badRequests = []

def put(item): 
    if 'bgn' in item:
        item['bgn'] = item['bgn'].isoformat()
    if 'end' in item:
        item['end'] = item['end'].isoformat()
        
    k = str(item.pop('_id', ObjectId()))
    domain.put_attributes(k, item, replace = False)

pool = Pool(30)

for i in sample:
    global count
    global badRequests
    try:
        count += 1 
        pool.spawn(put,i)
        if count % 1000 == 0:
            print count, time.time()
    except: 
        badRequests.append(i)
        
pool.join()

print "Now attempting bad requests"

#Attempts bad reqeusts up until 1000 additional failures and then exits, printing a list of the bad requests left unadded
for i in badRequests:
    global failures
    global badRequests
    try:
        pool.spawn(put,i)
    except: 
        failures += 1
        if failures > 1000:
            print badRequests
            break
        else:
            badRequests.append(i)

pool.join()


