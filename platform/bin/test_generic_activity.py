#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from datetime           import datetime
from Schemas            import *
from MongoStampedAPI    import MongoStampedAPI

user_id = "4e57048dccc2175fca000005"

request = SuggestedUserRequest(dict(
    limit           = 5, 
    personalized    = True, 
))

api     = MongoStampedAPI()
users   = api.getSuggestedUsers(user_id, request)

for (user, explanations) in users:
    subject0 = 'Stamped thinks you might be interested in '
    subject1 = user.screen_name
    subject2 = '\'s tastes.'
    subject  = subject0 + subject1 + subject2
    ls0      = len(subject0)
    indices  = (ls0, ls0 + len(subject1))
    usermini = user.exportSchema(UserMini())
    user_id2 = user.user_id
    
    
    api._addActivity(
        genre           = 'generic', 
        user_id         = user_id, # TODO: should this be user_id2? gets overwritten by kwargs anyway..
        recipient_ids   = [ user_id ], 
        user            = usermini, 
        icon            = 'http://static.stamped.com/assets/activity/follower.png', 
        subject         = subject, 
        subject_objects = [ { 'user_id' : user_id2, 'indices' : indices } ], 
        blurb           = ' and '.join(explanations), 
        link            = dict(
            linked_user = usermini, 
            linked_user_id = user_id2, 
        ))

