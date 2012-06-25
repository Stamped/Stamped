#!/usr/bin/env python
"""
    Account creation functions
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *
from errors             import *
from HTTPSchemas        import *
from Netflix            import *
from Facebook           import *

@handleHTTPRequest(requires_auth=False, 
                   requires_client=True, 
                   http_schema=HTTPAccountNew, 
                   conversion=HTTPAccountNew.convertToAccount,
                   upload='profile_image',
                   parse_request_kwargs={'obfuscate':['password' ]})
@require_http_methods(["POST"])
def create(request, client_id, http_schema, schema, **kwargs):
    try:
        account = stampedAPI.addAccount(schema, tempImageUrl=http_schema.temp_image_url)
    except StampedInvalidEmailError:
        raise StampedHTTPError(400, msg="Invalid email address")
    except StampedInvalidScreenNameError:
        raise StampedHTTPError(400, msg="Invalid screen name")
    except StampedDuplicateEmailError:
        raise StampedHTTPError(409, msg="An account already exists with that email address")
    except StampedDuplicateScreenNameError:
        raise StampedHTTPError(409, msg="An account already exists with that screen name")

    user   = HTTPUser().importAccount(account)
    logs.user(user.user_id)
    
    token  = stampedAuth.addRefreshToken(client_id, user.user_id)
    output = { 'user': user.dataExport(), 'token': token }
    
    return transformOutput(output)

# upgrade account from third party auth to stamped auth
@handleHTTPRequest(requires_client=True,
                   http_schema=HTTPAccountUpgradeForm,
                   parse_request_kwargs={'obfuscate':['password']})
@require_http_methods(["POST"])
def upgrade(request, client_id, authUserId, http_schema, **kwargs):
    account = stampedAPI.upgradeAccount(authUserId, http_schema.email, http_schema.password)

    user   = HTTPUser().importAccount(account)

    token  = stampedAuth.addRefreshToken(client_id, user.user_id)
    output = { 'user': user.dataExport(), 'token': token }

    return transformOutput(output)

@handleHTTPRequest(requires_auth=False,
                   requires_client=True,
                   http_schema=HTTPFacebookAccountNew,
                   conversion=HTTPFacebookAccountNew.convertToFacebookAccountNew,
                   parse_request_kwargs={'obfuscate':['user_token']})
@require_http_methods(["POST"])
def createWithFacebook(request, client_id, http_schema, schema, **kwargs):
    try:
        account = stampedAPI.addFacebookAccount(schema, tempImageUrl=http_schema.temp_image_url)
    except StampedLinkedAccountExistsError:
        raise StampedHTTPError(409, msg="An account already exists for this Facebook user")
    except StampedInvalidEmailError:
        raise StampedHTTPError(400, msg="Invalid email address")
    except StampedInvalidScreenNameError:
        raise StampedHTTPError(400, msg="Invalid screen name")
    except StampedDuplicateEmailError:
        raise StampedHTTPError(409, msg="An account already exists with that email address")
    except StampedDuplicateScreenNameError:
        raise StampedHTTPError(409, msg="An account already exists with that screen name")

    user   = HTTPUser().importAccount(account)
    logs.user(user.user_id)

    token  = stampedAuth.addRefreshToken(client_id, user.user_id)
    output = { 'user': user.dataExport(), 'token': token }

    return transformOutput(output)

@handleHTTPRequest(requires_auth=False,
                   requires_client=True,
                   http_schema=HTTPTwitterAccountNew,
                   conversion=HTTPTwitterAccountNew.convertToTwitterAccountNew,
                   parse_request_kwargs={'obfuscate':['user_token', 'user_secret']})
@require_http_methods(["POST"])
def createWithTwitter(request, client_id, http_schema, schema, **kwargs):
    try:
        account = stampedAPI.addTwitterAccount(schema, tempImageUrl=http_schema.temp_image_url)
    except StampedLinkedAccountExistsError:
        raise StampedHTTPError(409, msg="An account already exists for this Twitter user")
    except StampedInvalidEmailError:
        raise StampedHTTPError(400, msg="Invalid email address")
    except StampedInvalidScreenNameError:
        raise StampedHTTPError(400, msg="Invalid screen name")
    except StampedDuplicateEmailError:
        raise StampedHTTPError(409, msg="An account already exists with that email address")
    except StampedDuplicateScreenNameError:
        raise StampedHTTPError(409, msg="An account already exists with that screen name")

    user   = HTTPUser().importAccount(account)
    logs.user(user.user_id)

    token  = stampedAuth.addRefreshToken(client_id, user.user_id)
    output = { 'user': user.dataExport(), 'token': token }

    return transformOutput(output)

@handleHTTPRequest()
@require_http_methods(["POST"])
def remove(request, authUserId, **kwargs):
    account = stampedAPI.removeAccount(authUserId)
    if account is None:
        raise StampedIllegalActionError('Could not find account for provided authUserId')
    account = HTTPAccount().importAccount(account)
    
    return transformOutput(account.dataExport())


@handleHTTPRequest(parse_request=False)
@require_http_methods(["GET"])
def show(request, authUserId, **kwargs):
    account = stampedAPI.getAccount(authUserId)
    print(account)
    if account is None:
        logs.warning('Could not find account for authUserId')
        raise StampedIllegalActionError('There was an error retrieving account information')
    account = HTTPAccount().importAccount(account)

    return transformOutput(account.dataExport())

@handleHTTPRequest(http_schema=HTTPAccountUpdateForm,
                   conversion=HTTPAccountUpdateForm.convertToAccountUpdateForm)
@require_http_methods(["POST"])
def update(request, authUserId, http_schema, schema, **kwargs):
    account = stampedAPI.updateAccount(authUserId, schema)

    user    = HTTPUser().importUser(account)
    return transformOutput(user.dataExport())

#@handleHTTPRequest(parse_request=False)
#@require_http_methods(["POST"])
#def update(request, authUserId, **kwargs):x
#    ### TODO: Carve out password changes, require original password sent again?
#
#    ### TEMP: Generate list of changes. Need to do something better eventually..
#    schema = parseRequest(HTTPAccountSettings(), request)
#    data   = schema.dataExport()
#
#    for k, v in data.iteritems():
#        if v == '':
#            data[k] = None
#
#    ### TODO: Verify email is valid
#    account = stampedAPI.updateAccountSettings(authUserId, data)
#
#    account     = HTTPAccount().importAccount(account)
#
#    return transformOutput(account.dataExport())

#@handleHTTPRequest(http_schema=HTTPAccountProfile)
#@require_http_methods(["POST"])
#def updateProfile(request, authUserId, data, **kwargs):
#    ### TEMP: Generate list of changes. Need to do something better eventually...
#    for k, v in data.iteritems():
#        if v == '':
#            data[k] = None
#
#    account = stampedAPI.updateProfile(authUserId, data)
#    user    = HTTPUser().importUser(account)
#
#    return transformOutput(user.dataExport())


@handleHTTPRequest(http_schema=HTTPAccountProfileImage)
@require_http_methods(["POST"])
def updateProfileImage(request, authUserId, http_schema, **kwargs):
    user = stampedAPI.updateProfileImage(authUserId, http_schema.temp_image_url)
    user = HTTPUser().importUser(user)

    return transformOutput(user.dataExport())


@handleHTTPRequest(http_schema=HTTPCustomizeStamp)
@require_http_methods(["POST"])
def customizeStamp(request, authUserId, data, **kwargs):
    account = stampedAPI.customizeStamp(authUserId, data)
    user    = HTTPUser().importUser(account)
    
    return transformOutput(user.dataExport())

@handleHTTPRequest(requires_auth=False, 
                   requires_client=True, 
                   http_schema=HTTPAccountCheck)
@require_http_methods(["POST"])
def check(request, client_id, http_schema, **kwargs):
    try:
        user = stampedAPI.checkAccount(http_schema.login)
        user = HTTPUser().importUser(user)
        
        ### TODO: REMOVE THIS TEMPORARY CONVERSION!!!!
        try:
            if str(http_schema.login).lower() == str(user.screen_name).lower():
                user.screen_name = str(http_schema.login)
        except Exception as e:
            logs.warning("Exception: %s" % e)
        
        return transformOutput(user.dataExport())
    except KeyError:
        response = HttpResponse("not_found")
        response.status_code = 404
        return response
    except Exception:
        response = HttpResponse("invalid_request")
        response.status_code = 400
        return response


@handleHTTPRequest(http_schema=HTTPAccountChangePassword, 
                   parse_request_kwargs={'obfuscate':['old_password', 'new_password']})
@require_http_methods(["POST"])
def changePassword(request, authUserId, http_schema, **kwargs):
    new = http_schema.new_password
    old = http_schema.old_password
    
    try:
        stampedAuth.verifyPassword(authUserId, old)
    except StampedInvalidCredentialsError:
        raise StampedHTTPError(401, kind="invalid_credentials")

    result = stampedAuth.updatePassword(authUserId, new)
    
    return transformOutput(True)


@handleHTTPRequest(requires_auth=False, http_schema=HTTPEmail)
@require_http_methods(["POST"])
def resetPassword(request, client_id, http_schema, **kwargs):
    stampedAuth.resetPassword(http_schema.email)

    return transformOutput(True)


@handleHTTPRequest()
@require_http_methods(["GET"])
def showAlerts(request, authUserId, **kwargs):
    account  = stampedAPI.getAccount(authUserId)
    settings = HTTPAccountAlerts().importAccount(account)

    return transformOutput(settings.dataExport())


@handleHTTPRequest(http_schema=HTTPAccountAlerts)
@require_http_methods(["POST"])
def updateAlerts(request, authUserId, http_schema, **kwargs):
    account  = stampedAPI.updateAlerts(authUserId, http_schema)
    settings = HTTPAccountAlerts().importAccount(account)

    return transformOutput(settings.dataExport())


@handleHTTPRequest(http_schema=HTTPAPNSToken)
@require_http_methods(["POST"])
def updateApns(request, authUserId, http_schema, **kwargs):
    if len(http_schema.token) != 64:
        raise StampedInputError('Invalid token length')
    
    stampedAPI.updateAPNSToken(authUserId, http_schema.token)
    return transformOutput(True)


@handleHTTPRequest(http_schema=HTTPAPNSToken)
@require_http_methods(["POST"])
def removeApns(request, authUserId, http_schema, **kwargs):
    if len(http_schema.token) != 64:
        raise StampedInputError('Invalid token length')
    
    stampedAPI.removeAPNSTokenForUser(authUserId, http_schema.token)
    return transformOutput(True)

