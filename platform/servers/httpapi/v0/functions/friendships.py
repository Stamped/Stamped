#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from servers.httpapi.v0.helpers import *

friendshipExceptions = [
    (StampedInvalidFriendshipError, 400, "not_found", "You cannot follow yourself."),
    (StampedFriendshipCheckPermissionsError, 404, "not_found", "Insufficient privileges to check friendship status."),
    (StampedInviteAlreadyExistsError, 403, "illegal_action", "Invite already sent."),
    (StampedUnknownSourceError, 400, "bad_request", "Unknown source name"),
]

@require_http_methods(["POST"])
@handleHTTPRequest(http_schema=HTTPUserId, exceptions=friendshipExceptions)
def create(request, authUserId, http_schema, **kwargs):
    user = stampedAPI.friendships.addFriendship(authUserId, http_schema)
    user = HTTPUser().importUser(user)
    
    return transformOutput(user.dataExport())


@require_http_methods(["POST"])
@handleHTTPRequest(http_schema=HTTPUserId, exceptions=friendshipExceptions)
def remove(request, authUserId, http_schema, **kwargs):
    user = stampedAPI.friendships.removeFriendship(authUserId, http_schema)
    user = HTTPUser().importUser(user)
    
    return transformOutput(user.dataExport())


@require_http_methods(["GET"])
@handleHTTPRequest(http_schema=HTTPUserRelationship, exceptions=friendshipExceptions)
def check(request, authUserId, http_schema, **kwargs):
    result = stampedAPI.friendships.checkFriendship(authUserId, http_schema)
    
    return transformOutput(result)


@require_http_methods(["GET"])
@handleHTTPRequest(requires_auth=False, http_schema=HTTPUserId, exceptions=friendshipExceptions)
def friends(request, authUserId, http_schema, **kwargs):
    userIds = stampedAPI.friendships.getFriends(http_schema)
    output  = { 'user_ids' : userIds }
    
    return transformOutput(output)


@require_http_methods(["GET"])
@handleHTTPRequest(requires_auth=False, http_schema=HTTPUserId, exceptions=friendshipExceptions)
def followers(request, authUserId, http_schema, **kwargs):
    userIds = stampedAPI.friendships.getFollowers(http_schema)
    output  = { 'user_ids': userIds }
    
    return transformOutput(output)


@require_http_methods(["POST"])
@handleHTTPRequest(http_schema=HTTPEmails, exceptions=friendshipExceptions)
def invite(request, authUserId, http_schema, **kwargs):
    emails = http_schema.emails.split(',')
    result = stampedAPI.friendships.inviteFriends(authUserId, emails)

    return transformOutput(True)

