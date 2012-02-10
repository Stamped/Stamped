#!/usr/bin/python

import stamped, utils
import time

from api.MongoStampedAPI    import MongoStampedAPI
from api.Schemas            import *

api = MongoStampedAPI()
user_ids = [ 
    "4e57048dccc2175fca000005", 
    "4e57048accc2175fcd000001", 
    "4e57048bccc2175fcd000002", 
    "4e570490ccc2175fcd000003", 
    "4e985cc7fe4a1d2fc4000220", 
    "4e98f376fe4a1d44dd00014c", 
    "4eca8dd5112dea0809000182", 
    "4ecb8f5534083316d300254b", 
]

for user_id in user_ids:
    s = FriendsSlice()
    
    print "%s" % user_id
    
    for distance in xrange(5):
        s.distance  = distance
        s.inclusive = True
        
        t0   = time.time()
        ret0 = api._collectionDB.getFriendsStampIds(user_id, s)
        t1   = time.time()
        dur  = (t1 - t0) * 1000.0
        
        print "%d) %d (%s seconds)" % (distance, len(ret0), dur)
        
        t0   = time.time()
        ret1 = api._collectionDB.getFriendsStampIds2(user_id, s)
        t1   = time.time()
        dur  = (t1 - t0) * 1000.0
        
        print "%d) %d (%s seconds)" % (distance, len(ret1), dur)

