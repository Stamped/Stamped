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
def timeout(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(None, request)

    time.sleep(55)

@handleHTTPRequest
@require_http_methods(["GET"])
def ping(request):
    return transformOutput(True)



