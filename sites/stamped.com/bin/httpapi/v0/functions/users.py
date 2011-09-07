#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from httpapi.v0.helpers import *

@handleHTTPRequest
@require_http_methods(["GET"])
def show(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    user        = stampedAPI.getUser(schema, authUserId)
    user        = HTTPUser().importSchema(user)

    return transformOutput(user.exportSparse())


@handleHTTPRequest
@require_http_methods(["GET"])
def lookup(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserIds(), request)

    users       = stampedAPI.getUsers(schema.user_ids.value, \
                    schema.screen_names.value, authUserId)

    output = []
    for user in users:
        output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["GET"])
def search(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserSearch(), request)

    users       = stampedAPI.searchUsers(schema.q, schema.limit, authUserId)

    output = []
    for user in users:
        output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["GET"])
def privacy(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    privacy     = stampedAPI.getPrivacy(schema)

    return transformOutput(privacy)


@handleHTTPRequest
@require_http_methods(["GET"])
def findEmail(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPFindUser(), request)

    users       = stampedAPI.findUsersByEmail(authUserId, schema.q.value)

    output = []
    for user in users:
        output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["GET"])
def findPhone(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPFindUser(), request)

    users       = stampedAPI.findUsersByPhone(authUserId, schema.q.value)

    output = []
    for user in users:
        output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(output)

