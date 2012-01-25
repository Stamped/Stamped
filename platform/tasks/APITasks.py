#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils
import logs

from celery.task import task

__stamped_api__ = None

def getStampedAPI():
    """ hack to ensure that tasks only instantiate the Stamped API once """
    
    import Globals
    from api.MongoStampedAPI import MongoStampedAPI
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

def invoke(*args, **kwargs):
    """ 
        wrapper to invoke a stamped api function in an asynchronous context 
        which adds logging and exception handling.
    """
    
    try:
        stampedAPI = getStampedAPI()
        
        logs.begin(
            addLog=stampedAPI._logsDB.addLog, 
            saveLog=stampedAPI._logsDB.saveLog,
            saveStat=stampedAPI._statsDB.addStat,
            nodeName=stampedAPI.node_name,
        )
        
        func = "%sAsync" % utils.getFuncName(1)
        logs.info("%s %s %s" % (func, args, kwargs))
        f=open('/stamped/temp', 'w')
        f.write("%s %s %s" % (func, args, kwargs))
        f.close()
        
        getattr(stampedAPI, func)(*args, **kwargs)
    except Exception as e:
        logs.error(str(e))
        raise
    """finally:
        try:
            logs.save()
        except:
            pass
            """

@task(ignore_result=True)
def addStamp(*args, **kwargs):
    invoke(*args, **kwargs)

@task(ignore_result=True)
def addResizedStampImages(*args, **kwargs):
    invoke(*args, **kwargs)

@task(ignore_result=True)
def customizeStamp(*args, **kwargs):
    invoke(*args, **kwargs)

@task(ignore_result=True)
def updateProfileImage(*args, **kwargs):
    invoke(*args, **kwargs)

@task(ignore_result=True)
def addAccount(*args, **kwargs):
    invoke(*args, **kwargs)

@task(ignore_result=True)
def updateAccountSettings(*args, **kwargs):
    invoke(*args, **kwargs)

@task(ignore_result=True)
def alertFollowersFromTwitter(*args, **kwargs):
    invoke(*args, **kwargs)

@task(ignore_result=True)
def alertFollowersFromFacebook(*args, **kwargs):
    invoke(*args, **kwargs)

@task(ignore_result=True)
def addFriendship(*args, **kwargs):
    invoke(*args, **kwargs)

@task(ignore_result=True)
def removeFriendship(*args, **kwargs):
    invoke(*args, **kwargs)

@task(ignore_result=True)
def inviteFriend(*args, **kwargs):
    invoke(*args, **kwargs)

@task(ignore_result=True)
def addComment(*args, **kwargs):
    invoke(*args, **kwargs)

