#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils
import logs

from optparse    import OptionParser
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

def invoke(request, *args, **kwargs):
    """ 
        wrapper to invoke a stamped api function in an asynchronous context 
        which adds logging and exception handling.
    """
    
    try:
        stampedAPI = getStampedAPI()
        func = "%sAsync" % utils.getFuncName(1)
        
        if not request.is_eager:
            logs.begin(
                #addLog=stampedAPI._logsDB.addLog, 
                saveLog=stampedAPI._logsDB.saveLog,
                saveStat=stampedAPI._statsDB.addStat,
                nodeName=stampedAPI.node_name,
            )
            
            logs.async_request(func, *args, **kwargs)
        
        logs.info("%s %s %s (is_eager=%s, hostname=%s, task_id=%s)" % 
                  (func, args, kwargs, request.is_eager, request.hostname, request.id))
        
        getattr(stampedAPI, func)(*args, **kwargs)
    except Exception as e:
        logs.error(str(e))
        raise
    finally:
        try:
            if not request.is_eager:
                logs.save()
        except:
            pass

default_params = {
    'ignore_result'         : True,
}

retry_params = {
    'ignore_result'         : True,
    'default_retry_delay'   : 10, 
    'max_retries'           : 3,
}

# Image Manipulation

@task(queue='api', **retry_params)
def addResizedStampImages(*args, **kwargs):
    invoke(addResizedStampImages.request, *args, **kwargs)

@task(queue='api', **retry_params)
def customizeStamp(*args, **kwargs):
    invoke(customizeStamp.request, *args, **kwargs)

@task(queue='api', **retry_params)
def updateProfileImage(*args, **kwargs):
    invoke(updateProfileImage.request, *args, **kwargs)

# Stamped API

@task(queue='api', **default_params)
def addAccount(*args, **kwargs):
    invoke(addAccount.request, *args, **kwargs)

@task(queue='api', **default_params)
def changeProfileImageName(*args, **kwargs):
    invoke(changeProfileImageName.request, *args, **kwargs)

@task(queue='api', **default_params)
def alertFollowersFromTwitter(*args, **kwargs):
    invoke(alertFollowersFromTwitter.request, *args, **kwargs)

@task(queue='api', **default_params)
def alertFollowersFromFacebook(*args, **kwargs):
    invoke(alertFollowersFromFacebook.request, *args, **kwargs)

@task(queue='api', **default_params)
def addFriendship(*args, **kwargs):
    invoke(addFriendship.request, *args, **kwargs)

@task(queue='api', **retry_params)
def removeFriendship(*args, **kwargs):
    invoke(removeFriendship.request, *args, **kwargs)

@task(queue='api', **default_params)
def inviteFriends(*args, **kwargs):
    invoke(inviteFriend.request, *args, **kwargs)

@task(queue='api', **default_params)
def updateEntityStats(*args, **kwargs):
    invoke(updateEntityStats.request, *args, **kwargs)

@task(queue='api', **default_params)
def completeAction(*args, **kwargs):
    invoke(completeAction.request, *args, **kwargs)

@task(queue='api', **default_params)
def addStamp(*args, **kwargs):
    invoke(addStamp.request, *args, **kwargs)

@task(queue='api', **default_params)
def removeStamp(*args, **kwargs):
    invoke(removeStamp.request, *args, **kwargs)

@task(queue='api', **default_params)
def updateStampStats(*args, **kwargs):
    invoke(updateStampStats.request, *args, **kwargs)

@task(queue='api', **default_params)
def addComment(*args, **kwargs):
    invoke(addComment.request, *args, **kwargs)

@task(queue='api', **default_params)
def addLike(*args, **kwargs):
    invoke(addLike.request, *args, **kwargs)

@task(queue='api', **default_params)
def getComments(*args, **kwargs):
    invoke(getComments.request, *args, **kwargs)

@task(queue='api', **default_params)
def addTodo(*args, **kwargs):
    invoke(addTodo.request, *args, **kwargs)

@task(queue='api', **default_params)
def postToOpenGraph(*args, **kwargs):
    invoke(postToOpenGraph.request, *args, **kwargs)

@task(queue='api', **default_params)
def buildGuide(*args, **kwargs):
    invoke(buildGuide.request, *args, **kwargs)

@task(queue='api', **default_params)
def updateTombstonedEntityReferences(*args, **kwargs):
    invoke(updateTombstonedEntityReferences.request, *args, **kwargs)

# Enrichment

@task(queue='enrich', **default_params)
def mergeEntity(*args, **kwargs):
    invoke(mergeEntity.request, *args, **kwargs)

@task(queue='enrich', **default_params)
def mergeEntityId(*args, **kwargs):
    invoke(mergeEntityId.request, *args, **kwargs)

# Collage

@task(queue='enrich', **default_params)
def updateUserImageCollage(*args, **kwargs):
    invoke(updateUserImageCollage.request, *args, **kwargs)



def parseCommandLine():
    usage   = "Usage: %prog [options]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    return parser.parse_args()

def main():
    options, args = parseCommandLine()
    
    if len(args) >= 1:
        utils.log("running %s%s" % (args[0], tuple(args[1:])))
        
        eval("%s(*args[1:])" % (args[0], ))

if __name__ == '__main__':
    main()

