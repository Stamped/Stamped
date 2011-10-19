#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import time
from httpapi.v0.helpers import *

@handleHTTPRequest
@require_http_methods(["GET"])
def friends(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    userIds     = stampedAPI.getFriends(schema)
    users       = stampedAPI.getUsers(userIds, None, authUserId)

    output = []
    for user in users:
        output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["GET"])
def followers(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    userIds     = stampedAPI.getFollowers(schema)
    users       = stampedAPI.getUsers(userIds, None, authUserId)

    output = []
    for user in users:
        output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["GET"])
def activity(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPGenericSlice(), request)

    activity    = stampedAPI.getActivity(authUserId, **schema.exportSparse())
    
    result = []
    for item in activity:
        # result.append(HTTPActivity().importSchema(item).exportSparse())
        
        ### TEMP
        stamp = None
        if item.linked_stamp != None:
            stamp = item.linked_stamp

        comment = None
        if item.linked_comment_id != None:
            comment = stampedAPI._getComment(item.linked_comment_id)

        result.append(HTTPActivityOld().importSchema(item, stamp, comment).exportSparse())

    return transformOutput(result)

@handleHTTPRequest
@require_http_methods(["GET"])
def inbox(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPGenericSlice(), request)

    data        = schema.exportSparse()
    data['godMode'] = True
    stamps      = stampedAPI.getInboxStamps(authUserId, **data)

    result = []
    for stamp in stamps:
        if 'deleted' in stamp:
            result.append(HTTPDeletedStamp().importSchema(stamp).exportSparse())
        else:
            result.append(HTTPStamp().importSchema(stamp).exportSparse())

    return transformOutput(result)

@handleHTTPRequest
@require_http_methods(["GET"])
def timeout(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(None, request)

    time.sleep(55)









@handleHTTPRequest
@require_http_methods(["GET"])
def static(request):
    return transformOutput(True)


def addEntity():
    entity = Entity()
    entity.title = 'SAMPLE TITLE'
    entity.subtitle = 'SAMPLE SUBTITLE'
    entity.category = 'other'
    entity.subcategory = 'other'

    result = stampedAPI.addEntity(entity)
    return result['entity_id']


@handleHTTPRequest
@require_http_methods(["GET"])
def begin(request):
    result = addEntity()
    return transformOutput(result)


@handleHTTPRequest
@require_http_methods(["GET"])
def read(request):
    entityIds = request.GET['entity_ids'].split(',')
    output = []
    for entityId in entityIds:
        print entityId
        result = stampedAPI.getEntity({'entity_id': entityId})
        output.append(HTTPEntity().importSchema(result).exportSparse())
    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["GET"])
def write(request):
    n = int(request.GET['n'])
    output = []
    for i in xrange(n):
        result = addEntity()
        output.append(result)
    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["GET"])
def readwrite(request):
    output = []

    entityIds = request.GET['entity_ids'].split(',')
    for entityId in entityIds:
        result = stampedAPI.getEntity({'entity_id': entityId})
        output.append(HTTPEntity().importSchema(result).exportSparse())

    n = int(request.GET['n'])
    for i in xrange(n):
        result = addEntity()
        output.append(result)

    return transformOutput(output)






