#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals
import utils

from celery.task    import task

__stamped_api__     = None

def getStampedAPI():
    """ hack to ensure that tasks only instantiate the Stamped API once """
    
    from MongoStampedAPI import MongoStampedAPI
    global __stamped_api__
    
    if __stamped_api__ is None:
        __stamped_api__ = MongoStampedAPI()
    
    return __stamped_api__

@task
def add(x, y):
    msg = ("Executing task id %r, args: %r kwargs: %r" % (
            add.request.id, add.request.args, add.request.kwargs))
    utils.log(msg)
    
    return x + y

@task(ignore_result=True)
def addStamp(user_id, stamp_id):
    stampedAPI = getStampedAPI()
    followers  = stampedAPI._friendshipDB.getFollowers(user_id)
    
    stampedAPI._stampDB.addInboxStampReference(followers, stamp_id)

