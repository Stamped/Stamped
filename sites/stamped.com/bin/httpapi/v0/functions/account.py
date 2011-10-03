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
    
    # suffix      = '.jpg'
    
    # images = { }
    # prefixes = {
    #     'fast' : 'static.stamped.com/', 
    #     'slow' : 'http://stamped.com.static.images.s3.amazonaws.com/', 
    # }
    
    # for k, prefix in prefixes.iteritems():
    #     prefix = "%s/users/%s" % (prefix, authUserId)
    #     value  = []
        
    #     value.append("%s%s" % (prefix, suffix))
    #     value.append("%s-144x144%s" % (prefix, suffix))
    #     value.append("%s-72x72%s" % (prefix, suffix))
    #     value.append("%s-110x110%s" % (prefix, suffix))
    #     value.append("%s-55x55%s" % (prefix, suffix))
    #     value.append("%s-92x92%s" % (prefix, suffix))
    #     value.append("%s-46x46%s" % (prefix, suffix))
    #     value.append("%s-74x74%s" % (prefix, suffix))
    #     value.append("%s-37x37%s" % (prefix, suffix))
    #     value.append("%s-62x62%s" % (prefix, suffix))
    #     value.append("%s-31x31%s" % (prefix, suffix))
    #     images[k] = value
    
    # output      = { 'user_id': authUserId, 'images': images, }
    
    # return transformOutput(output)


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
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPLinkedAccounts(), request)
    linked      = schema.exportSchema(LinkedAccounts())
    
    result      = stampedAPI.updateLinkedAccounts(authUserId, linked)
    
    return transformOutput(True)


@handleHTTPRequest
@require_http_methods(["POST"])
def change_password(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPAccountChangePassword(), request, \
                    obfuscate=['old_password', 'new_password'])
    new         = schema.new_password
    old         = schema.old_password

    stampedAuth.verifyPassword(authUserId, old)

    result      = stampedAPI.updatePassword(authUserId, new)

    return transformOutput(True)


@handleHTTPRequest
@require_http_methods(["POST"])
def reset_password(request):
    raise NotImplementedError

