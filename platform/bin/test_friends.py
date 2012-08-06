#!/usr/bin/env python
from __future__ import absolute_import

import Globals, utils
import time

from api.MongoStampedAPI    import MongoStampedAPI
from api.Schemas            import *

api = MongoStampedAPI()
user_ids = [ 
    "4e57048dccc2175fca000005", 
    #"4e57048accc2175fcd000001", 
    #"4e57048bccc2175fcd000002", 
    #"4e570490ccc2175fcd000003", 
    #"4e985cc7fe4a1d2fc4000220", 
    #"4e98f376fe4a1d44dd00014c", 
    #"4eca8dd5112dea0809000182", 
    #"4ecb8f5534083316d300254b", 
]

for user_id in user_ids:
    s = FriendsSlice()
    
    print "%s" % user_id
    
    #for distance in xrange(5):
    distance    = 2
    s.distance  = distance
    s.inclusive = True
    
    t0   = time.time()
    ret0 = api.getFriendsStamps(user_id, s)
    t1   = time.time()
    dur0 = (t1 - t0)
    
    print "%d) %d (%s seconds)" % (distance, len(ret0), dur0)
    for stamp in ret0:
        print stamp
    
    """
    t0   = time.time()
    ret1 = api._collectionDB.getFriendsStampIds2(user_id, s)
    t1   = time.time()
    dur1 = (t1 - t0)
    
    warn = " WARNING" if (dur1 > dur0) else ""
    print "%d) %d (%s seconds)%s" % (distance, len(ret1), dur1, warn)
    
    t0   = time.time()
    ret2 = api._collectionDB.getFriendsStampIds3(user_id, s)
    t1   = time.time()
    dur2 = (t1 - t0)
    
    warn = " WARNING" if (dur2 > dur0) else ""
    print "%d) %d (%s seconds)%s" % (distance, len(ret2), dur2, warn)
    """

