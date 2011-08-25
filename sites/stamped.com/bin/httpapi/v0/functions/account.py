#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from httpapi.v0.helpers import *

@handleHTTPRequest
@require_http_methods(["POST"])
def create(request):
    client_id   = checkClient(request)
    schema      = parseRequest(HTTPAccountNew(), request)
    account     = schema.exportSchema(Account())

    account     = stampedAPI.addAccount(account)
    user        = HTTPUser().importSchema(account)

    token       = stampedAuth.addRefreshToken(client_id, user.user_id)

    output      = { 'user': user.exportSparse(), 'token': token }

    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["POST"])
def remove(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(None, request)

    account     = stampedAPI.removeAccount(authUserId)
    account     = HTTPAccount().importSchema(account)

    return transformOutput(account.exportSparse())


@handleHTTPRequest
@require_http_methods(["POST", "GET"])
def settings(request):
    authUserId  = checkOAuth(request)

    if request.method == 'POST':

        ### TODO: Carve out password changes, require original password sent again?

        ### TEMP: Generate list of changes. Need to do something better eventually..
        schema      = parseRequest(HTTPAccountSettings(), request)
        data        = schema.exportSparse()

        for k, v in data.iteritems():
            if v == '':
                data[k] = None

        ### TODO: Verify email is valid
        account     = stampedAPI.updateAccountSettings(authUserId, data)

    else:
        schema      = parseRequest(None, request)
        account     = stampedAPI.getAccount(authUserId)

    account     = HTTPAccount().importSchema(account)

    return transformOutput(account.exportSparse())


@handleHTTPRequest
@require_http_methods(["POST"])
def update_profile(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPAccountProfile(), request)

    ### TEMP: Generate list of changes. Need to do something better eventually...
    data        = schema.exportSparse()

    for k, v in data.iteritems():
        if v == '':
            data[k] = None

    if 'color' in data:
        color = data['color'].split(',')
        data['color_primary']   = color[0]
        data['color_secondary'] = color[-1]
        del(data['color'])
    
    account     = stampedAPI.updateProfile(authUserId, data)
    user        = HTTPUser().importSchema(account)

    return transformOutput(user.exportSparse())


@handleHTTPRequest
@require_http_methods(["POST"])
def update_profile_image(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPAccountProfileImage(), request)
    
    url         = stampedAPI.updateProfileImage(authUserId, schema.profile_image)

    output      = { 'user_id': authUserId, 'profile_image': url }

    return transformOutput(output)


@handleHTTPRequest
@require_http_methods(["POST"])
def verify_credentials(request):
    raise NotImplementedError


@handleHTTPRequest
@require_http_methods(["POST"])
def reset_password(request):
    raise NotImplementedError





