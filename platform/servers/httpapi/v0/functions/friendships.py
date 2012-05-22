#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *

@handleHTTPRequest(http_schema=HTTPUserId)
@require_http_methods(["POST"])
def create(request, authUserId, http_schema, **kwargs):
    user = stampedAPI.addFriendship(authUserId, http_schema)
    user = HTTPUser().importUser(user)
    
    return transformOutput(user.dataExport())


@handleHTTPRequest(http_schema=HTTPUserId)
@require_http_methods(["POST"])
def remove(request, authUserId, http_schema, **kwargs):
    user = stampedAPI.removeFriendship(authUserId, http_schema)
    user = HTTPUser().importUser(user)
    
    return transformOutput(user.dataExport())


@handleHTTPRequest(http_schema=HTTPUserRelationship)
@require_http_methods(["GET"])
def check(request, authUserId, http_schema, **kwargs):
    result = stampedAPI.checkFriendship(authUserId, http_schema)
    
    return transformOutput(result)


@handleHTTPRequest(requires_auth=False, 
                   http_schema=HTTPUserId)
@require_http_methods(["GET"])
def friends(request, authUserId, http_schema, **kwargs):
    userIds = stampedAPI.getFriends(http_schema)
    output  = { 'user_ids' : userIds }
    
    return transformOutput(output)


@handleHTTPRequest(requires_auth=False, 
                   http_schema=HTTPUserId)
@require_http_methods(["GET"])
def followers(request, authUserId, http_schema, **kwargs):
    userIds = stampedAPI.getFollowers(http_schema)
    output  = { 'user_ids': userIds }
    
    return transformOutput(output)


@handleHTTPRequest(http_schema=HTTPUserId)
@require_http_methods(["POST"])
def approve(request, authUserId, http_schema, **kwargs):
    user = stampedAPI.approveFriendship(authUserId, http_schema)
    user = HTTPUser().importUser(user)

    return transformOutput(user.dataExport())


@handleHTTPRequest(http_schema=HTTPUserId)
@require_http_methods(["POST"])
def blocksCreate(request, authUserId, http_schema, **kwargs):
    user = stampedAPI.addBlock(authUserId, http_schema)
    user = HTTPUser().importUser(user)
    
    return transformOutput(user.dataExport())


@handleHTTPRequest(http_schema=HTTPUserId)
@require_http_methods(["GET"])
def blocksCheck(request, authUserId, http_schema, **kwargs):
    result = stampedAPI.checkBlock(authUserId, http_schema)

    return transformOutput(result)


@handleHTTPRequest()
@require_http_methods(["GET"])
def blocking(request, authUserId, **kwargs):
    userIds = stampedAPI.getBlocks(authUserId)
    output  = { 'user_ids' : userIds }
    
    return transformOutput(output)


@handleHTTPRequest(http_schema=HTTPUserId)
@require_http_methods(["POST"])
def blocksRemove(request, authUserId, http_schema, **kwargs):
    user = stampedAPI.removeBlock(authUserId, http_schema)
    user = HTTPUser().importUser(user)
    
    return transformOutput(user.dataExport())


@handleHTTPRequest(http_schema=HTTPEmail)
@require_http_methods(["POST"])
def invite(request, authUserId, http_schema, **kwargs):
    result = stampedAPI.inviteFriend(authUserId, http_schema.email)

    return transformOutput(True)

