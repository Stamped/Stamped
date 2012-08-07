#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils
import logs
import datetime
import time

from optparse    import OptionParser
from celery.task import task

__stamped_api__ = None

def getStampedAPI():
    """ hack to ensure that tasks only instantiate the Stamped API once """
    
    import Globals
    from api_old.MongoStampedAPI import MongoStampedAPI
    global __stamped_api__
    
    if __stamped_api__ is None:
        __stamped_api__ = MongoStampedAPI()
    
    return __stamped_api__


def invoke(request, *args, **kwargs):
    """ 
        wrapper to invoke a stamped api function in an asynchronous context 
        which adds logging and exception handling.
    """
    
    taskId = kwargs.pop('taskId', None)

    try:
        stampedAPI = getStampedAPI()
        func = "%sAsync" % utils.getFuncName(1)
        
        if not request.is_eager:
            logs.begin(
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
            if taskId is not None:
                stampedAPI._asyncTasksDB.removeTask(taskId)
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
    invoke(inviteFriends.request, *args, **kwargs)

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
def updateFBPermissions(*args, **kwargs):
    invoke(updateFBPermissions.request, *args, **kwargs)

@task(queue='api', **default_params)
def postToOpenGraph(*args, **kwargs):
    invoke(postToOpenGraph.request, *args, **kwargs)

@task(queue='api', **default_params)
def deleteFromOpenGraph(*args, **kwargs):
    invoke(deleteFromOpenGraph.request, *args, **kwargs)

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

@task(queue='enrich', **default_params)
def crawlExternalSources(*args, **kwargs):
    invoke(crawlExternalSources.request, *args, **kwargs)

@task(queue='enrich', **default_params)
def updateAutoCompleteIndex(*args, **kwargs):
    invoke(updateAutoCompleteIndex.request, *args, **kwargs)

# Collage

@task(queue='enrich', **default_params)
def updateUserImageCollage(*args, **kwargs):
    invoke(updateUserImageCollage.request, *args, **kwargs)

from boto.s3.connection import S3Connection
from boto.s3.key import Key
import keys.aws
from contextlib import closing

# TODO PULL OUT TO SOMEWHERE COMMON (copied from AutoCompleteIndex)
def getS3Key(filename):
    BUCKET_NAME = 'stamped.com.static.images'

    conn = S3Connection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
    bucket = conn.create_bucket(BUCKET_NAME)
    key = bucket.get_key(filename)
    if key is None:
        key = bucket.new_key(filename)
    return key

def findAmicablePairsNaive(n):
    def sumOfDivisors(i):
        s = 0
        for j in range(1, i):
            if i % j == 0:
                s += j
        return s
    results = []
    for i in range(n):
        for j in range(i):
            if sumOfDivisors(i) == j and i == sumOfDivisors(j):
                results.append((i, j))
    print results


@task(queue='enrich', **retry_params)
def enrichQueueFindAmicablePairsNaive(n, **garbage):
    findAmicablePairsNaive(n)


@task(queue='api', **retry_params)
def apiQueueFindAmicablePairsNaive(n, **garbage):
    findAmicablePairsNaive(n)


def writeTimestampToS3(s3_filename, request_id):
    logs.debug('Writing timestamp to S3 file %s' % s3_filename)
    file_content = '%s: %s' % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), request_id)
    delay = 0.1
    max_delay = 3
    max_tries = 40
    for i in range(max_tries):
        try:
            with closing(getS3Key(s3_filename)) as key:
                key.set_contents_from_string(file_content)
                key.set_acl('private')
                return
        except:
            time.sleep(delay)
            delay = min(max_delay, delay*1.5)
    raise Exception('Failed 40 fucking times. How does that even happen.')

@task(queue='enrich', **retry_params)
def enrichQueueWriteTimestampToS3(s3_filename, **garbage):
    writeTimestampToS3(s3_filename, enrichQueueWriteTimestampToS3.request.id)

@task(queue='api', **retry_params)
def apiQueueWriteTimestampToS3(s3_filename, **garbage):
    writeTimestampToS3(s3_filename, apiQueueWriteTimestampToS3.request.id)


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

