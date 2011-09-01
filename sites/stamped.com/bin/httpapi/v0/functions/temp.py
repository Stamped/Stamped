#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

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
        if item.stamp_id != None:
            stamp = stampedAPI.getStamp(item.stamp_id, authUserId)

        comment = None
        if item.comment_id != None:
            comment = stampedAPI._getComment(item.comment_id)

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
        result.append(HTTPStamp().importSchema(stamp).exportSparse())

    return transformOutput(result)