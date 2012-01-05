#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *

@handleHTTPRequest
@require_http_methods(["POST"])
def create(request):
    client_id   = checkClient(request)
    schema      = parseFileUpload(HTTPAccountNew(), request, 'profile_image')
    account     = schema.exportSchema(Account())

    account     = stampedAPI.addAccount(account, schema.profile_image)
    user        = HTTPUser().importSchema(account)
    logs.user(user.user_id)

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
    
    account     = stampedAPI.updateProfile(authUserId, data)
    user        = HTTPUser().importSchema(account)

    return transformOutput(user.exportSparse())


@handleHTTPRequest
@require_http_methods(["POST"])
def update_profile_image(request):
    authUserId  = checkOAuth(request)
    schema      = parseFileUpload(HTTPAccountProfileImage(), request, 'profile_image')
    
    user        = stampedAPI.updateProfileImage(authUserId, schema.profile_image)
    user        = HTTPUser().importSchema(user)
    
    return transformOutput(user.exportSparse())


@handleHTTPRequest
@require_http_methods(["POST"])
def customize_stamp(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPCustomizeStamp(), request)
    data        = schema.exportSparse()
    
    account     = stampedAPI.customizeStamp(authUserId, data)
    user        = HTTPUser().importSchema(account)

    return transformOutput(user.exportSparse())


@handleHTTPRequest
@require_http_methods(["POST"])
def check(request):
    client_id   = checkClient(request)
    schema      = parseRequest(HTTPAccountCheck(), request)

    try:
        user    = stampedAPI.checkAccount(schema.login)
        user    = HTTPUser().importSchema(user)

        ### TODO: REMOVE THIS TEMPORARY CONVERSION!!!!
        try:
            if str(schema.login).lower() == str(user.screen_name).lower():
                user.screen_name = str(schema.login)
        except:
            pass

        return transformOutput(user.exportSparse())
    except KeyError:
        response = HttpResponse("not_found")
        response.status_code = 404
        return response
    except Exception:
        response = HttpResponse("invalid_request")
        response.status_code = 400
        return response


@handleHTTPRequest
@require_http_methods(["POST"])
def linked_accounts(request):
    authUserId      = checkOAuth(request)
    schema          = parseRequest(HTTPLinkedAccounts(), request)

    linked          = schema.exportSchema(LinkedAccounts())
    twitterAuth     = schema.exportSchema(TwitterAuthSchema())
    facebookAuth    = schema.exportSchema(FacebookAuthSchema())

    data = {
        'twitter': linked.twitter,
        'facebook': linked.facebook,
        'twitterAuth': twitterAuth,
        'facebookAuth': facebookAuth,
    }
    stampedAPI.updateLinkedAccounts(authUserId, **data)
    
    return transformOutput(True)


@handleHTTPRequest
@require_http_methods(["POST"])
def removeTwitter(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(None, request)

    result = stampedAPI.removeLinkedAccount(authUserId, 'twitter')
    
    return transformOutput(True)


@handleHTTPRequest
@require_http_methods(["POST"])
def removeFacebook(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(None, request)

    result = stampedAPI.removeLinkedAccount(authUserId, 'facebook')
    
    return transformOutput(True)


@handleHTTPRequest
@require_http_methods(["POST"])
def alertFollowersFromTwitter(request):
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

    result      = stampedAPI.alertFollowersFromTwitter(authUserId, twitterIds)
    
    return transformOutput(result)


@handleHTTPRequest
@require_http_methods(["POST"])
def alertFollowersFromFacebook(request):
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

    result      = stampedAPI.alertFollowersFromFacebook(authUserId, facebookIds)
    
    return transformOutput(result)


@handleHTTPRequest
@require_http_methods(["POST"])
def change_password(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPAccountChangePassword(), request, \
                    obfuscate=['old_password', 'new_password'])
    new         = schema.new_password
    old         = schema.old_password

    stampedAuth.verifyPassword(authUserId, old)

    result      = stampedAuth.updatePassword(authUserId, new)

    return transformOutput(True)


@handleHTTPRequest
@require_http_methods(["POST"])
def reset_password(request):
    client_id   = checkClient(request)
    schema      = parseRequest(HTTPEmail(), request)

    stampedAuth.resetPassword(schema.email)

    return transformOutput(True)


@handleHTTPRequest
@require_http_methods(["GET"])
def show_alerts(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(None, request)
    
    account     = stampedAPI.getAccount(authUserId)
    settings    = HTTPAccountAlerts().importSchema(account)

    return transformOutput(settings.value)


@handleHTTPRequest
@require_http_methods(["POST"])
def update_alerts(request):
    authUserId  = checkOAuth(request)
    alerts      = parseRequest(HTTPAccountAlerts(), request)
    
    account     = stampedAPI.updateAlerts(authUserId, alerts)
    settings    = HTTPAccountAlerts().importSchema(account)

    return transformOutput(settings.value)


@handleHTTPRequest
@require_http_methods(["POST"])
def update_apns(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPAPNSToken(), request)

    if len(schema.token) != 64:
        raise InputError('Invalid token length')
    
    stampedAPI.updateAPNSToken(authUserId, schema.token)
    return transformOutput(True)


@handleHTTPRequest
@require_http_methods(["POST"])
def remove_apns(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPAPNSToken(), request)

    if len(schema.token) != 64:
        raise InputError('Invalid token length')
    
    stampedAPI.removeAPNSTokenForUser(authUserId, schema.token)
    return transformOutput(True)

