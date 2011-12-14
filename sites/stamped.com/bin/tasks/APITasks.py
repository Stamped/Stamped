#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals
import utils

from celery.task import task

__stampedapi__ = None

def getStampedAPI():
    from MongoStampedAPI import MongoStampedAPI
    global __stampedapi__
    
    if __stampedapi__ is None:
        __stampedapi__ = MongoStampedAPI()
    
    return __stampedapi__

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

