#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *
import time

@handleHTTPRequest(http_schema=HTTPUserId)
@require_http_methods(["GET"])
def friends(request, authUserId, http_schema, **kwargs):
    userIds = stampedAPI.getFriends(http_schema)
    users   = stampedAPI.getUsers(userIds, None, authUserId)
    
    output = []
    for user in users:
        output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(output)


@handleHTTPRequest(http_schema=HTTPUserId)
@require_http_methods(["GET"])
def followers(request, authUserId, http_schema, **kwargs):
    userIds = stampedAPI.getFollowers(http_schema)
    users   = stampedAPI.getUsers(userIds, None, authUserId)

    output = []
    for user in users:
        output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(output)


@handleHTTPRequest()
@require_http_methods(["GET"])
def timeout(request, authUserId, **kwargs):
    schema = parseRequest(None, request)
    
    time.sleep(55)

