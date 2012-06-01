#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *

@handleHTTPRequest(requires_auth=False, 
                   http_schema=HTTPUserId)
@require_http_methods(["GET"])
def show(request, authUserId, http_schema, **kwargs):
    user = stampedAPI.getUser(http_schema, authUserId)
    user = HTTPUser().importUser(user)
    
    return transformOutput(user.dataExport())


@handleHTTPRequest(requires_auth=False, 
                   http_schema=HTTPUserIds)
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


@handleHTTPRequest(http_schema=HTTPUserSearch)
@require_http_methods(["POST"])
def search(request, authUserId, http_schema, **kwargs):
    users  = stampedAPI.searchUsers(authUserId, 
                                    http_schema.q, 
                                    http_schema.limit, 
                                    http_schema.relationship)
    
    output = []
    for user in users:
        if user.user_id != authUserId:
            output.append(HTTPUser().importUser(user).dataExport())
    
    return transformOutput(output)


@handleHTTPRequest(http_schema=HTTPSuggestedUserRequest, 
                   conversion=HTTPSuggestedUserRequest.convertToSuggestedUserRequest)
@require_http_methods(["GET"])
def suggested(request, authUserId, schema, **kwargs):
    results = stampedAPI.getSuggestedUsers(authUserId, schema)
    output  = []
    
    if schema.personalized:
        for user, explanations in results:
            user2 = HTTPSuggestedUser().importUser(user).dataExport()
            user2.explanations = explanations
            output.append(user2)
    else:
        for user in results:
            user2 = HTTPSuggestedUser().importUser(user).dataExport()
            output.append(user2)
    
    return transformOutput(output)


@handleHTTPRequest(http_schema=HTTPUserId)
@require_http_methods(["GET"])
def privacy(request, authUserId, http_schema, **kwargs):
    privacy = stampedAPI.getPrivacy(http_schema)
    
    return transformOutput(privacy)


@handleHTTPRequest(http_schema=HTTPFindUser, parse_request_kwargs={'obfuscate':['q']})
@require_http_methods(["POST"])
def findEmail(request, authUserId, http_schema, **kwargs):
    q = http_schema.q.split(',')
    emails = []
    
    for email in q:
        try:
            emails.append(email.decode('ascii'))
        except:
            msg = 'Invalid email: %s' % email
            logs.warning(msg)
    
    users       = stampedAPI.findUsersByEmail(authUserId, emails)
    
    output = []
    for user in users:
        if user.user_id != authUserId:
            output.append(HTTPUser().importUser(user).dataExport())
    
    return transformOutput(output)


@handleHTTPRequest(http_schema=HTTPFindUser, parse_request_kwargs={'obfuscate':['q']})
@require_http_methods(["POST"])
def findPhone(request, authUserId, http_schema, **kwargs):
    q = http_schema.q.split(',')
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
            output.append(HTTPUser().importUser(user).dataExport())
    
    return transformOutput(output)


@handleHTTPRequest(http_schema=HTTPFindTwitterUser, 
                   parse_request_kwargs={'obfuscate':['user_token', 'user_secret' ]})
@require_http_methods(["POST"])
def findTwitter(request, authUserId, http_schema, **kwargs):
    users = stampedAPI.findUsersByTwitter(authUserId,
                                          twitterKey=http_schema.user_token,
                                          twitterSecret=http_schema.user_secret)
    output = []
    for user in users:
        if user.user_id != authUserId:
            output.append(HTTPUser().importUser(user).dataExport())
    
    return transformOutput(output)


@handleHTTPRequest(http_schema=HTTPFindFacebookUser, 
                   parse_request_kwargs={'obfuscate':['user_token' ]})
@require_http_methods(["POST"])
def findFacebook(request, authUserId, http_schema, **kwargs):
    users = stampedAPI.findUsersByFacebook(authUserId, facebookToken=http_schema.facebook_token)

    output = [HTTPUser().importUser(user).dataExport() for user in users if user.user_id != authUserId]
    return transformOutput(output)

