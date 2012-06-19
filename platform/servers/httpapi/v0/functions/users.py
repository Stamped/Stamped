#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *

@handleHTTPRequest(requires_auth=False, http_schema=HTTPUserId)
@require_http_methods(["GET"])
def show(request, authUserId, http_schema, **kwargs):
    user = stampedAPI.getUser(http_schema, authUserId)
    user = HTTPUser().importUser(user)
    
    return transformOutput(user.dataExport())


@handleHTTPRequest(requires_auth=False, http_schema=HTTPUserIds)
@require_http_methods(["POST"])
def lookup(request, authUserId, http_schema, **kwargs):
    if http_schema.user_ids is not None:
        users = stampedAPI.getUsers(http_schema.user_ids.split(','), None, authUserId)
    elif http_schema.screen_names is not None:
        users = stampedAPI.getUsers(None, http_schema.screen_names.split(','), authUserId)
    else:
        raise Exception("Field missing")
    
    output = []
    for user in users:
        output.append(HTTPUser().importUser(user).dataExport())
    
    return transformOutput(output)

@handleHTTPRequest(requires_auth=False, http_schema=HTTPUserId)
@require_http_methods(["GET"])
def images(request, authUserId, http_schema, **kwargs):
    user = stampedAPI.getUser(http_schema, authUserId)
    images = HTTPUserImages().importUser(user)
    return transformOutput(images.dataExport())


@handleHTTPRequest(http_schema=HTTPUserSearch)
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


@handleHTTPRequest(http_schema=HTTPSuggestedUserRequest)
@require_http_methods(["GET"])
def suggested(request, authUserId, http_schema, **kwargs):
    users = stampedAPI.getSuggestedUsers(authUserId, limit=http_schema.limit, offset=http_schema.offset)
    output  = []

    for user in users:
        suggested = HTTPSuggestedUser().importUser(user).dataExport()
        output.append(suggested)

    return transformOutput(output)


@handleHTTPRequest(http_schema=HTTPUserId)
@require_http_methods(["GET"])
def privacy(request, authUserId, http_schema, **kwargs):
    privacy = stampedAPI.getPrivacy(http_schema)
    
    return transformOutput(privacy)


@handleHTTPRequest(http_schema=HTTPFindUser, parse_request_kwargs={'obfuscate':['query']})
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

    users       = stampedAPI.findUsersByEmail(authUserId, emails)

    output = []
    for user in users:
        if user.user_id != authUserId:
            output.append(HTTPSuggestedUser().importUser(user).dataExport())
    
    return transformOutput(output)


@handleHTTPRequest(http_schema=HTTPFindUser, parse_request_kwargs={'obfuscate':['query']})
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


@handleHTTPRequest(http_schema=HTTPFindTwitterUser, 
                   parse_request_kwargs={'obfuscate':['user_token', 'user_secret' ]})
@require_http_methods(["POST"])
def findTwitter(request, authUserId, http_schema, **kwargs):
    users = stampedAPI.findUsersByTwitter(authUserId, http_schema.user_token, http_schema.user_secret)
    output = []
    for user in users:
        if user.user_id != authUserId:
            output.append(HTTPSuggestedUser().importUser(user).dataExport())
    
    return transformOutput(output)


@handleHTTPRequest(http_schema=HTTPFindFacebookUser, 
                   parse_request_kwargs={'obfuscate':['user_token' ]})
@require_http_methods(["POST"])
def findFacebook(request, authUserId, http_schema, **kwargs):
    users = stampedAPI.findUsersByFacebook(authUserId, http_schema.user_token)

    output = [HTTPSuggestedUser().importUser(user).dataExport() for user in users if user.user_id != authUserId]
    return transformOutput(output)

