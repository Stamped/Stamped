#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *

exceptions = [
    (StampedDocumentNotFoundError, StampedHTTPError(404, kind="not_found", msg="There was a problem retrieving the requested data.")),
    (StampedMissingParametersError, StampedHTTPError(400, kind='bad_request', msg="Missing parameters: user ids or screen names required")),
    (StampedAccountNotFoundError, StampedHTTPError(404, kind='not_found', msg='There was an error retrieving account information')),
    (StampedViewUserPermissionsError, StampedHTTPError(403, kind='forbidden', msg='Insufficient privileges to view user')),
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


exceptions_findTwitter = [(StampedThirdPartyInvalidCredentialsError, StampedHTTPError(403, kind='invalid_credentials', msg='Invalid Twitter credentials')) ]
@handleHTTPRequest(http_schema=HTTPFindTwitterUser, 
                   parse_request_kwargs={'obfuscate':['user_token', 'user_secret' ]},
                   exceptions=exceptions + exceptions_findTwitter)
@require_http_methods(["POST"])
def findTwitter(request, authUserId, http_schema, **kwargs):
    users = stampedAPI.findUsersByTwitter(authUserId, http_schema.user_token, http_schema.user_secret)
    output = []
    for user in users:
        if user.user_id != authUserId:
            output.append(HTTPSuggestedUser().importUser(user).dataExport())
    
    return transformOutput(output)


exceptions_findFacebook = [(StampedThirdPartyInvalidCredentialsError, StampedHTTPError(403, kind='invalid_credentials', msg='Invalid Facebook credentials')) ]
@handleHTTPRequest(http_schema=HTTPFindFacebookUser, 
                   parse_request_kwargs={'obfuscate':['user_token' ]},
                   exceptions=exceptions + exceptions_findFacebook)
@require_http_methods(["POST"])
def findFacebook(request, authUserId, http_schema, **kwargs):
    users = stampedAPI.findUsersByFacebook(authUserId, http_schema.user_token)

    output = [HTTPSuggestedUser().importUser(user).dataExport() for user in users if user.user_id != authUserId]
    return transformOutput(output)


exceptions_inviteFacebookCollection = [(StampedThirdPartyInvalidCredentialsError, StampedHTTPError(403, kind='invalid_credentials', msg='Invalid Facebook credentials')) ]
@handleHTTPRequest(http_schema=HTTPFacebookFriendsCollectionForm,
    parse_request_kwargs={'obfuscate':['user_token' ]},
    exceptions=exceptions + exceptions_inviteFacebookCollection)
@require_http_methods(["POST"])
def inviteFacebookCollection(request, authUserId, http_schema, **kwargs):
    linked = stampedAPI.getLinkedAccount(authUserId, 'facebook')
    if linked.token is None:
        raise StampedMissingLinkedAccountTokenError("No facebook access token associated with linked account")

    offset = 0 if http_schema.offset is None else http_schema.offset
    limit = 30 if http_schema.offset is None else http_schema.offset
    logs.info('### linked.token: %s    offset: %s   limit: %s' % (linked.token, offset, limit))
    result = stampedAPI.getFacebookFriendData(linked.token, offset, limit)
    return transformOutput(result)
