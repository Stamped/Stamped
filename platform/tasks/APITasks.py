#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils

from celery.task import task

__stamped_api__ = None

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
def addStamp(*args, **kwargs):
    getStampedAPI().addStampAsync(*args, **kwargs)

@task(ignore_result=True)
def addResizedStampImages(*args, **kwargs):
    getStampedAPI().addResizedStampImagesAsync(*args, **kwargs)

@task(ignore_result=True)
def customizeStamp(*args, **kwargs):
    getStampedAPI().customizeStampAsync(*args, **kwargs)

@task(ignore_result=True)
def updateProfileImage(*args, **kwargs):
    getStampedAPI().updateProfileImageAsync(*args, **kwargs)

@task(ignore_result=True)
def addAccount(*args, **kwargs):
    getStampedAPI().addAccountAsync(*args, **kwargs)

@task(ignore_result=True)
def updateAccountSettings(*args, **kwargs):
    getStampedAPI().updateAccountSettingsAsync(*args, **kwargs)

@task(ignore_result=True)
def alertFollowersFromTwitter(*args, **kwargs):
    getStampedAPI().alertFollowersFromTwitterAsync(*args, **kwargs)

@task(ignore_result=True)
def alertFollowersFromFacebook(*args, **kwargs):
    getStampedAPI().alertFollowersFromFacebookAsync(*args, **kwargs)

@task(ignore_result=True)
def addFriendship(*args, **kwargs):
    getStampedAPI().addFriendshipAsync(*args, **kwargs)

@task(ignore_result=True)
def removeFriendship(*args, **kwargs):
    getStampedAPI().removeFriendshipAsync(*args, **kwargs)

@task(ignore_result=True)
def inviteFriend(*args, **kwargs):
    getStampedAPI().inviteFriendAsync(*args, **kwargs)

@task(ignore_result=True)
def addComment(*args, **kwargs):
    getStampedAPI().addCommentAsync(*args, **kwargs)

