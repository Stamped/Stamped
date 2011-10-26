#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *

@handleHTTPRequest
@require_http_methods(["POST"])
def create(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    user        = stampedAPI.addFriendship(authUserId, schema)
    user        = HTTPUser().importSchema(user)

    return transformOutput(user.exportSparse())


@handleHTTPRequest
@require_http_methods(["POST"])
def remove(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    user        = stampedAPI.removeFriendship(authUserId, schema)
    user        = HTTPUser().importSchema(user)

    return transformOutput(user.exportSparse())


@handleHTTPRequest
@require_http_methods(["GET"])
def check(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserRelationship(), request)

    result      = stampedAPI.checkFriendship(authUserId, schema)

    return transformOutput(result)


@handleHTTPRequest
@require_http_methods(["GET"])
def friends(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    userIds     = stampedAPI.getFriends(schema)
    output      = { 'user_ids': userIds }

    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["GET"])
def followers(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    userIds     = stampedAPI.getFollowers(schema)
    output      = { 'user_ids': userIds }

    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["POST"])
def approve(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    user        = stampedAPI.approveFriendship(authUserId, schema)
    user        = HTTPUser().importSchema(user)

    return transformOutput(user.exportSparse())


@handleHTTPRequest
@require_http_methods(["POST"])
def blocksCreate(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    user        = stampedAPI.addBlock(authUserId, schema)
    user        = HTTPUser().importSchema(user)

    return transformOutput(user.exportSparse())


@handleHTTPRequest
@require_http_methods(["GET"])
def blocksCheck(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    result      = stampedAPI.checkBlock(authUserId, schema)

    return transformOutput(result)


@handleHTTPRequest
@require_http_methods(["GET"])
def blocking(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(None, request)

    userIds     = stampedAPI.getBlocks(authUserId)
    output      = { 'user_ids': userIds }

    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["POST"])
def blocksRemove(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    user        = stampedAPI.removeBlock(authUserId, schema)
    user        = HTTPUser().importSchema(user)

    return transformOutput(user.exportSparse())


@handleHTTPRequest
@require_http_methods(["POST"])
def invite(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPEmail(), request)

    result      = stampedAPI.inviteFriend(authUserId, schema.email)

    return transformOutput(True)


