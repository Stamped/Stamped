import Globals

import sys
import keys.aws, logs, utils
from api.MongoStampedAPI import MongoStampedAPI
import boto
from api.db.mongodb.MongoStatsCollection            import MongoStatsCollection
from bson.objectid          import ObjectId
from gevent.pool import Pool
import sha


conn = boto.connect_sdb("AKIAJPJJ2QXCMPIITWDQ","XwBv06/ezFEjsJvalbLNgE9IrHJ46DlGtWc5/F+X")
#domain = conn.get_domain('stats_dev')

api = MongoStampedAPI()
sample = MongoStatsCollection()._collection.find()

def putMongo(item,destination): 
    
    if 'bgn' in item:
        item['bgn'] = item['bgn'].isoformat()
    if 'end' in item:
        item['end'] = item['end'].isoformat()
        
    k = str(item.pop('_id', ObjectId()))
    destination.put_attributes(k, item, replace = False)


def mongoToSDB(origin, destination):
    count = 0
    failures = 0
    badRequests = []
    
    pool = Pool(30)
    
    for i in origin:

        try: 
            pool.spawn(putMongo,i,destination)
            count += 1
            if count % 1000 == 0:
                print count
        except: 
            badRequests.append(i)
            
    pool.join()
    
    print "Now attempting bad requests"
    
    #Attempts bad reqeusts up until 1000 additional failures and then exits, printing a list of the bad requests left unadded
    for i in badRequests:
        try:
            pool.spawn(putMongo,i,destination)
        except: 
            failures += 1
            if failures > 1000:
                print badRequests
                break
            else:
                badRequests.append(i)
    
    pool.join()
    
def putSDB(item,suffix): 
    global queues
    global domains
    
    queues[suffix][item.name] = item
    
    if len(queues[suffix]) >= 24:
        domains[suffix].batch_put_attributes(queues[suffix], replace = False)
        queues[suffix] = {}

def SDBToSDB(origins,destination,domains,origNum):
    place = 0
    count = 0
    failures = 0
    badRequests = []
    pings_ignored = 0
    
    suffix = '0'+hex(origNum)[2]
    
    for i in origins[suffix]:
        if place > 0:
            try:
                if i['uri'] == "/v0/ping.json" or i['uri'] == '/v0/temp/ping.json':
                    pings_ignored += 1
                    if pings_ignored % 500 == 0:
                        print 'ignored: ' + str(pings_ignored)
                else: 
                    putSDB(i,suffix)
                    count += 1
                    if count % 1000 == 0:
                        print str(count) + ', ' + str(len(badRequests))
            except:
                badRequests.append(i)
        place += 1
        
    
    print "Now attempting bad requests"
    
    #Attempts bad reqeusts up until 1000 additional failures and then exits, printing a list of the bad requests left unadded
    for i in badRequests:
        dest = sha.new(i.name).hexdigest()[0]
        shard = destination + '_'+str(dest)
        try:
            pool.spawn(putSDB,i,shard)
        except: 
            failures += 1
            if failures > 1000:
                print badRequests
                break
            else:
                badRequests.append(i)
    
    pool.join()
    
    
origins = {}
domains = {}
queues = {}

for i in range (0,16):
    origins['0'+hex(i)[2]] = conn.get_domain('stats-prod_0'+hex(i)[2])

for i in range (0,16):
    queues['0'+hex(i)[2]] = {}

for i in range (0,16):
    domains['0'+hex(i)[2]] = conn.get_domain('stats_prod_0'+hex(i)[2])

pool = Pool(16)

for suffix in range (0,16):

    pool.spawn(SDBToSDB,origins,'stats_prod',domains,i) 
    
pool.join()


