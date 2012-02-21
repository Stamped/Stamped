#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

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
@require_http_methods(["POST"])
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
@require_http_methods(["POST"])
def search(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserSearch(), request)
    
    users       = stampedAPI.searchUsers(authUserId, schema.q, schema.limit, schema.relationship)
    
    output = []
    for user in users:
        if user.user_id != authUserId:
            output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["GET"])
def suggested(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPSuggestedUsers(), request).exportSchema(SuggestedUserRequest())
    
    results     = stampedAPI.getSuggestedUsers(authUserId, schema)
    output      = []
    
    if schema.personalized:
        for user, explanations in results:
            user2 = HTTPSuggestedUser().importSchema(user).exportSparse()
            user2.explanations = explanations
            output.append(user2)
    else:
        for user in results:
            user2 = HTTPSuggestedUser().importSchema(user).exportSparse()
            output.append(user2)
    
    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["GET"])
def privacy(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserId(), request)

    privacy     = stampedAPI.getPrivacy(schema)

    return transformOutput(privacy)


@handleHTTPRequest
@require_http_methods(["POST"])
def findEmail(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPFindUser(), request, obfuscate=['q'])

    q = schema.q.value
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
            output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["POST"])
def findPhone(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPFindUser(), request, obfuscate=['q'])

    q = schema.q.value
    phoneNumbers = []

    for item in q:
        try:
            if 11 == len(item) and item.startswith('1'):
                number = int(item[1:])
                phoneNumbers.append(item)
            
            number = int(item)
            phoneNumbers.append(item)
        except:
            msg = 'Invalid phone number: %s' % item
            logs.warning(msg)
    
    users       = stampedAPI.findUsersByPhone(authUserId, phoneNumbers)
    
    output = []
    for user in users:
        if user.user_id != authUserId:
            output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["POST"])
def findTwitter(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPFindTwitterUser(), request, obfuscate=['q', 'twitter_key', 'twitter_secret'])

    users = []

    if schema.twitter_key is not None and schema.twitter_secret is not None:
        users = stampedAPI.findUsersByTwitter(authUserId, 
                                              twitterKey=schema.twitter_key, 
                                              twitterSecret=schema.twitter_secret)

    elif schema.q is not None:
        q = schema.q.value

        twitterIds = []

        for item in q:
            try:
                number = int(item)
                twitterIds.append(item)
            except:
                msg = 'Invalid twitter id: %s' % item
                logs.warning(msg)

        users = stampedAPI.findUsersByTwitter(authUserId, twitterIds)

    output = []
    for user in users:
        if user.user_id != authUserId:
            output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["POST"])
def findFacebook(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPFindFacebookUser(), request, obfuscate=['q', 'facebook_token'])

    users = []

    if schema.facebook_token is not None:
        users = stampedAPI.findUsersByFacebook(authUserId, facebookToken=schema.facebook_token)

    elif schema.q is not None:
        q = schema.q.value
        facebookIds = []

        for item in q:
            try:
                number = int(item)
                facebookIds.append(item)
            except:
                msg = 'Invalid facebook id: %s' % item
                logs.warning(msg)

        users = stampedAPI.findUsersByFacebook(authUserId, facebookIds)

    output = []
    for user in users:
        if user.user_id != authUserId:
            output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(output)

