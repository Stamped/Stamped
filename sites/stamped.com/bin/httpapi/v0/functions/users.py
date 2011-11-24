#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
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

    users       = stampedAPI.searchUsers(schema.q, schema.limit, authUserId)

    output = []
    for user in users:
        if user.user_id != authUserId:
            output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["GET"])
def suggested(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(None, request)

    screenNames = ['mariobatali', 'petertravers', 'rebeccaminkoff', 'nymag', 'michaelkors']
    users       = stampedAPI.getUsers(None, screenNames, authUserId)
    logs.info('users: %s' % users)

    output = []
    for user in users:
        output.append(HTTPUser().importSchema(user).exportSparse())

    order = {'mariobatali':1, 'petertravers':2, 'nymag':3, 'rebeccaminkoff':4}
    output = sorted(output, key=lambda k: order[k['screen_name']])
    
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
    schema      = parseRequest(HTTPFindUser(), request, obfuscate=['q'])

    q = schema.q.value
    twitterIds = []

    for item in q:
        try:
            number = int(item)
            twitterIds.append(item)
        except:
            msg = 'Invalid twitter id: %s' % item
            logs.warning(msg)

    users       = stampedAPI.findUsersByTwitter(authUserId, twitterIds)

    output = []
    for user in users:
        if user.user_id != authUserId:
            output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["POST"])
def findFacebook(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPFindUser(), request, obfuscate=['q'])

    q = schema.q.value
    facebookIds = []

    for item in q:
        try:
            number = int(item)
            facebookIds.append(item)
        except:
            msg = 'Invalid facebook id: %s' % item
            logs.warning(msg)

    users       = stampedAPI.findUsersByFacebook(authUserId, facebookIds)

    output = []
    for user in users:
        if user.user_id != authUserId:
            output.append(HTTPUser().importSchema(user).exportSparse())
    
    return transformOutput(output)

