#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from servers.httpapi.v0.helpers import *

exceptions = [
    (StampedMissingParametersError, 400, 'bad_request', "Missing parameters: user ids or screen names required"),
    (StampedAccountNotFoundError, 404, 'not_found', 'There was an error retrieving account information'),
    (StampedViewUserPermissionsError, 403, 'forbidden', 'Insufficient privileges to view user'),
]


@handleHTTPRequest(requires_auth=False,
                   http_schema=HTTPUserId,
                   exceptions=exceptions)
@require_http_methods(["GET"])
def show(request, authUserId, http_schema, **kwargs):
    user = stampedAPI.getUser(http_schema, authUserId)
    user = HTTPUser().importUser(user)
    
    return transformOutput(user.dataExport())


@handleHTTPRequest(requires_auth=False,
                   http_schema=HTTPUserIds,
                   exceptions=exceptions)
@require_http_methods(["POST"])
def lookup(request, authUserId, http_schema, **kwargs):
    if http_schema.user_ids is not None:
        users = stampedAPI.getUsers(http_schema.user_ids.split(','), None, authUserId)
    elif http_schema.screen_names is not None:
        users = stampedAPI.getUsers(None, http_schema.screen_names.split(','), authUserId)
    else:
        raise StampedMissingParametersError("User ids or screen names required")
    
    output = []
    for user in users:
        output.append(HTTPUser().importUser(user).dataExport())
    
    return transformOutput(output)

@handleHTTPRequest(requires_auth=False,
                   http_schema=HTTPUserId,
                   exceptions=exceptions)
@require_http_methods(["GET"])
def images(request, authUserId, http_schema, **kwargs):
    user = stampedAPI.getUser(http_schema, authUserId)
    images = HTTPUserImages().importUser(user)
    return transformOutput(images.dataExport())


@handleHTTPRequest(http_schema=HTTPUserSearch,
                   exceptions=exceptions)
@require_http_methods(["POST"])
def search(request, authUserId, http_schema, **kwargs):
    users  = stampedAPI.searchUsers(authUserId, 
                                    http_schema.query, 
                                    http_schema.limit, 
                                    http_schema.relationship)
    
    output = []
    for user in users:
        if user.user_id != authUserId:
            output.append(HTTPUser().importUser(user).dataExport())
    
    return transformOutput(output)


@handleHTTPRequest(http_schema=HTTPSuggestedUserRequest,
                   exceptions=exceptions)
@require_http_methods(["GET"])
def suggested(request, authUserId, http_schema, **kwargs):
    users = stampedAPI.getSuggestedUsers(authUserId, limit=http_schema.limit, offset=http_schema.offset)
    output  = []

    for user in users:
        suggested = HTTPSuggestedUser().importUser(user).dataExport()
        output.append(suggested)

    return transformOutput(output)


@handleHTTPRequest(http_schema=HTTPUserId,
                   exceptions=exceptions)
@require_http_methods(["GET"])
def privacy(request, authUserId, http_schema, **kwargs):
    privacy = stampedAPI.getPrivacy(http_schema)
    
    return transformOutput(privacy)


@handleHTTPRequest(http_schema=HTTPFindUser,
                   parse_request_kwargs={'obfuscate':['query']},
                   exceptions=exceptions)
@require_http_methods(["POST"])
def findEmail(request, authUserId, http_schema, **kwargs):
    q = http_schema.query.split(',')
    emails = []
    
    for email in q:
        try:
            emails.append(email.decode('ascii'))
        except Exception:
            msg = 'Invalid email: %s' % email
            logs.warning(msg)

    users = stampedAPI.findUsersByEmail(authUserId, emails)

    output = []
    for user in users:
        if user.user_id != authUserId:
            output.append(HTTPSuggestedUser().importUser(user).dataExport())
    
    return transformOutput(output)


@handleHTTPRequest(http_schema=HTTPFindUser,
                   parse_request_kwargs={'obfuscate':['query']},
                   exceptions=exceptions)
@require_http_methods(["POST"])
def findPhone(request, authUserId, http_schema, **kwargs):
    q = http_schema.query.split(',')
    phoneNumbers = []
    
    for item in q:
        try:
            if 11 == len(item) and item.startswith('1'):
                number = int(item[1:])
                phoneNumbers.append(item)
            
            if len(item) <= 3:
                raise Exception
            
            number = int(item)
            phoneNumbers.append(item)
        except Exception:
            msg = 'Invalid phone number: %s' % item
            logs.warning(msg)
    
    users  = stampedAPI.findUsersByPhone(authUserId, phoneNumbers)
    
    output = []
    for user in users:
        if user.user_id != authUserId:
            output.append(HTTPSuggestedUser().importUser(user).dataExport())
    
    return transformOutput(output)


exceptions_findTwitter = [
    (StampedThirdPartyInvalidCredentialsError, 403, 'invalid_credentials', 'Invalid Twitter credentials'),
    (StampedMissingLinkedAccountTokenError, 400, "bad_request", "No Twitter login information associated with account"),
]
@handleHTTPRequest(exceptions=exceptions + exceptions_findTwitter)
@require_http_methods(["POST", "GET"])
def findTwitter(request, authUserId, http_schema, **kwargs):
    linked = stampedAPI.getLinkedAccount(authUserId, 'twitter')
    if linked.token is None or linked.secret is None:
        raise StampedMissingLinkedAccountTokenError("No twitter access token associated with linked account")

    users = stampedAPI.findUsersByTwitter(authUserId, linked.token, linked.secret)
    output = []
    for user in users:
        if user.user_id != authUserId:
            output.append(HTTPSuggestedUser().importUser(user).dataExport())
    
    return transformOutput(output)


exceptions_findFacebook = [
    (StampedThirdPartyInvalidCredentialsError, 403, 'invalid_credentials', 'Invalid Facebook credentials'),
    (StampedFacebookTokenError, 401, 'facebook_auth', "Facebook login failed. Please reauthorize your account."),
    (StampedMissingLinkedAccountTokenError, 400, "bad_request", "No Facebook login information associated with account"),
]
@handleHTTPRequest(exceptions=exceptions + exceptions_findFacebook)
@require_http_methods(["POST", "GET"])
def findFacebook(request, authUserId, http_schema, **kwargs):
    linked = stampedAPI.getLinkedAccount(authUserId, 'facebook')
    if linked.token is None:
        raise StampedMissingLinkedAccountTokenError("No facebook access token associated with linked account")

    users = stampedAPI.findUsersByFacebook(authUserId, linked.token)

    output = [HTTPSuggestedUser().importUser(user).dataExport() for user in users if user.user_id != authUserId]
    return transformOutput(output)


exceptions_inviteFacebookCollection = exceptions_findFacebook
@handleHTTPRequest(http_schema=HTTPFacebookFriendsCollectionForm,
                   exceptions=exceptions + exceptions_inviteFacebookCollection)
@require_http_methods(["GET"])
def inviteFacebookCollection(request, authUserId, http_schema, **kwargs):
    linked = stampedAPI.getLinkedAccount(authUserId, 'facebook')
    if linked.token is None:
        raise StampedMissingLinkedAccountTokenError("No facebook access token associated with linked account")

    offset = 0 if http_schema.offset is None else http_schema.offset
    limit = 30 if http_schema.limit is None else http_schema.limit

    result = stampedAPI.getFacebookFriendData(linked.token, offset, limit)
    return transformOutput(result)
