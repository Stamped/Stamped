#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from datetime           import datetime
from api_old.Schemas        import *
from api_old.MongoStampedAPI    import MongoStampedAPI

user_ids = set([ 
    #"4e57048dccc2175fca000005", # travis
    "4e57048accc2175fcd000001", # robby
    #"4e570489ccc2175fcd000000", # kevin
    #"4e57048bccc2175fcd000002", # bart
    #"4e57048eccc2175fca000006", # andybons
    #"4e57048cccc2175fca000003", # edmuki
    #"4eca8944e8ef21799d0001b3", # landon
])

request = SuggestedUserRequest(dict(
    limit           = 5, 
    personalized    = True, 
))

api     = MongoStampedAPI()
userDB  = api._userDB

rs = userDB._collection.find({'email' : { '$regex' : r'.*@stamped\.com', '$options' : 'i' }}, output=list)
for result in rs:
    user    = userDB._convertFromMongo(result)
    user_id = user.user_id
    
    if user_id not in user_ids:
        continue # only process team members
    
    utils.log('-' * 40)
    utils.log('%s) %s' % (user.screen_name, user_id))
    
    users   = api.getSuggestedUsers(user_id, request)
    
    for (user, explanations) in users:
        subject0 = 'Are you interested in '
        subject1 = user.screen_name
        subject2 = '\'s tastes?'
        subject  = subject0 + subject1 + subject2
        ls0      = len(subject0)
        indices  = [ ls0, ls0 + len(subject1) ]
        usermini = UserMini().dataImport(user.dataExport())
        user_id2 = user.user_id
        blurb    = ' and '.join(explanations)
        
        if blurb:
            blurb = blurb[0:1].title() + blurb[1:]
        
        utils.log("%s) %s" % (user, explanations))
        
        continue
        api._addActivity(
            genre           = 'generic', 
            user_id         = user_id, # TODO: should this be user_id2? gets overwritten by kwargs anyway..
            recipient_ids   = [ user_id ], 
            user            = usermini, 
            icon            = 'http://static.stamped.com/assets/activity/follower.png', 
            subject         = subject, 
            subject_objects = [ ActivityObjectSchema({ 'user_id' : user_id2, 'indices' : indices }) ], 
            blurb           = blurb, 
            linked_user_id  = user_id2)
    
    utils.log()
    utils.log()

