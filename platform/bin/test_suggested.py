#!/usr/bin/env python

import Globals, utils
import time

from api_old.MongoStampedAPI    import MongoStampedAPI
from api_old.Schemas            import *

api = MongoStampedAPI(lite_mode = True)
user_ids = [ 
    "4e57048dccc2175fca000005", # travis
    #"4e57048accc2175fcd000001", # robby
    #"4e570489ccc2175fcd000000", # kevin
    #"4e57048bccc2175fcd000002", # bart
    #"4e57048eccc2175fca000006", # andybons
    #"4e57048cccc2175fca000003", # edmuki
    #"4eca8944e8ef21799d0001b3", # landon
]

for user_id in user_ids:
    print "%s" % user_id
    
    request = SuggestedUserRequest(dict(personalized = True, limit=20))
    results = api._friendshipDB.getSuggestedUserIds(user_id, request)
    
    for result in results:
        user = api._userDB.getUser(result[0])
        print "%s (%s) %s" % (result[0], user.screen_name, result[1])

