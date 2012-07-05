#!/usr/bin/env python
"""
    Account creation functions
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from servers.httpapi.v0.helpers import *
from errors             import *
from api.HTTPSchemas        import *
from libs.Netflix       import *
from libs.Facebook           import *

#@handleHTTPRequest(requires_auth=False,
#                   requires_client=True,
#                   http_schema=HTTPAccountNew,
#                   conversion=HTTPAccountNew.convertToAccount,
#                   upload='profile_image',
#                   parse_request_kwargs={'obfuscate':['password']})
#@require_http_methods(["POST"])
#def create(request, client_id, http_schema, schema, **kwargs):
#    account = stampedAPI.addAccount(schema, tempImageUrl=http_schema.temp_image_url)
#
#    user   = HTTPUser().importAccount(account)
#    logs.user(user.user_id)
#
#    token  = stampedAuth.addRefreshToken(client_id, user.user_id)
#    output = { 'user': user.dataExport(), 'token': token }
#
#    return transformOutput(output)


exceptions = [
    (StampedInvalidEmailError,         400, 'invalid_credentials', "Invalid email address"),
    (StampedInvalidScreenNameError,    400, 'invalid_credentials', "Invalid screen name"),
    (StampedScreenNameInUseError,      400, 'invalid_credentials', "Screen name is already in use"),
    (StampedBlackListedScreenNameError, 403, 'forbidden',          'Invalid screen name'),
    (StampedInvalidPasswordError,      403, 'invalid_credentials', 'Incorrect password'),
    (StampedInvalidWebsiteError,       403, 'invalid_credentials', "Could not update account website"),
    (StampedInvalidStampColorsError,   403, 'invalid_credentials', "Invalid stamp colors"),
    (StampedDuplicateEmailError,       409, 'invalid_credentials', "An account already exists with that email address"),
    (StampedDuplicateScreenNameError,  409, 'invalid_credentials', "An account already exists with that screen name"),
    (StampedAccountNotFoundError,      404, 'not_found',           'There was an error retrieving account information'),
    (StampedAlreadyStampedAuthError,   400, 'bad_request',         'This account is already a Stamped account'),
    (StampedLinkedAccountMismatchError, 400, 'illegal_action',     "There was a problem verifying the third-party account"),
    (StampedUnsetRequiredFieldError,   400, 'illegal_action',      "Cannot remove a required account field"),
    (StampedEmailInUseError,           400, 'invalid_credentials', "Email address is already in use"),
]
exceptions_create = [(StampedInternalError,  400, 'internal', 'There was a problem creating the account. Please try again later.')]
@handleHTTPRequest(requires_auth=False,
                   requires_client=True,
                   http_schema=HTTPAccountNew,
                   conversion=HTTPAccountNew.convertToAccount,
                   upload='profile_image',
                   parse_request_kwargs={'obfuscate':['password']},
                   exceptions=exceptions)
@require_http_methods(["POST"])
def create(request, client_id, http_schema, schema, **kwargs):
    account = stampedAPI.addAccount(schema, tempImageUrl=http_schema.temp_image_url)

    user   = HTTPUser().importAccount(account)
    logs.user(user.user_id)

    token  = stampedAuth.addRefreshToken(client_id, user.user_id)
    output = { 'user': user.dataExport(), 'token': token }

    return transformOutput(output)

exceptions_update = [(StampedInternalError, 400, 'internal', 'There was a problem upgrading the account. Please try again later.')]
# upgrade account from third party auth to stamped auth
@handleHTTPRequest(requires_client=True,
                   http_schema=HTTPAccountUpgradeForm,
                   parse_request_kwargs={'obfuscate':['password']},
                   exceptions=exceptions + exceptions_update)
@require_http_methods(["POST"])
def upgrade(request, client_id, authUserId, http_schema, **kwargs):
    account = stampedAPI.upgradeAccount(authUserId, http_schema.email, http_schema.password)

    user   = HTTPUser().importAccount(account)

    token  = stampedAuth.addRefreshToken(client_id, user.user_id)
    output = { 'user': user.dataExport(), 'token': token }

    return transformOutput(output)


exceptions_createWithFacebook = [
    (StampedLinkedAccountAlreadyExistsError, 409, 'invalid_credentials', "An account already exists for this Facebook user"),
    (StampedThirdPartyError, 400, 'third_party', "There was an error connecting to Facebook"),
]
@handleHTTPRequest(requires_auth=False,
                   requires_client=True,
                   http_schema=HTTPFacebookAccountNew,
                   conversion=HTTPFacebookAccountNew.convertToFacebookAccountNew,
                   parse_request_kwargs={'obfuscate':['user_token']},
                   exceptions=exceptions + exceptions_createWithFacebook)
@require_http_methods(["POST"])
def createWithFacebook(request, client_id, http_schema, schema, **kwargs):
    account = stampedAPI.addFacebookAccount(schema, tempImageUrl=http_schema.temp_image_url)

    user   = HTTPUser().importAccount(account)
    logs.user(user.user_id)

    token  = stampedAuth.addRefreshToken(client_id, user.user_id)
    output = { 'user': user.dataExport(), 'token': token }

    return transformOutput(output)

exceptions_createWithTwitter = [
    (StampedLinkedAccountAlreadyExistsError, 409, 'invalid_credentials', "An account already exists for this Twitter user"),
    (StampedThirdPartyError, 400, 'third_party', "There was an error connecting to Twitter"),
]
@handleHTTPRequest(requires_auth=False,
                   requires_client=True,
                   http_schema=HTTPTwitterAccountNew,
                   conversion=HTTPTwitterAccountNew.convertToTwitterAccountNew,
                   parse_request_kwargs={'obfuscate':['user_token', 'user_secret']},
                   exceptions=exceptions + exceptions_createWithTwitter)
@require_http_methods(["POST"])
def createWithTwitter(request, client_id, http_schema, schema, **kwargs):
    account = stampedAPI.addTwitterAccount(schema, tempImageUrl=http_schema.temp_image_url)

    user   = HTTPUser().importAccount(account)
    logs.user(user.user_id)

    token  = stampedAuth.addRefreshToken(client_id, user.user_id)
    output = { 'user': user.dataExport(), 'token': token }

    return transformOutput(output)

@handleHTTPRequest()
@require_http_methods(["POST"])
def remove(request, authUserId, **kwargs):
    account = stampedAPI.removeAccount(authUserId)
    account = HTTPAccount().importAccount(account)

    return transformOutput(account.dataExport())


@handleHTTPRequest(parse_request=False,
                   exceptions=exceptions)
@require_http_methods(["GET"])
def show(request, authUserId, **kwargs):
    account = stampedAPI.getAccount(authUserId)
    account = HTTPAccount().importAccount(account)

    return transformOutput(account.dataExport())


exceptions_update = [(StampedInternalError, 400, 'internal', 'There was a problem updating the account.  Please try again later.')]
@handleHTTPRequest(http_schema=HTTPAccountUpdateForm,
                   conversion=HTTPAccountUpdateForm.convertToAccountUpdateForm,
                   exceptions=exceptions + exceptions_update)
@require_http_methods(["POST"])
def update(request, authUserId, http_schema, schema, **kwargs):
    logs.info('### http_schema: %s    schema: %s' % (http_schema, schema))
    account = stampedAPI.updateAccount(authUserId, schema)

    user    = HTTPUser().importUser(account)
    return transformOutput(user.dataExport())

@handleHTTPRequest(http_schema=HTTPCustomizeStamp,
                   exceptions=exceptions)
@require_http_methods(["POST"])
def customizeStamp(request, authUserId, data, **kwargs):
    account = stampedAPI.customizeStamp(authUserId, data)
    user    = HTTPUser().importUser(account)

    return transformOutput(user.dataExport())


@handleHTTPRequest(requires_auth=False,
                   requires_client=True,
                   http_schema=HTTPAccountCheck,
                   exceptions=exceptions)
@require_http_methods(["POST"])
def check(request, client_id, http_schema, **kwargs):
    user = stampedAPI.checkAccount(http_schema.login)
    user = HTTPUser().importUser(user)

    return transformOutput(user.dataExport())

@handleHTTPRequest(http_schema=HTTPAccountChangePassword,
                   parse_request_kwargs={'obfuscate':['old_password', 'new_password']})
@require_http_methods(["POST"])
def changePassword(request, authUserId, http_schema, **kwargs):
    new = http_schema.new_password
    old = http_schema.old_password

    stampedAuth.verifyPassword(authUserId, old)
    result = stampedAuth.updatePassword(authUserId, new)

    return transformOutput(True)


@handleHTTPRequest(requires_auth=False, http_schema=HTTPEmail)
@require_http_methods(["POST"])
def resetPassword(request, client_id, http_schema, **kwargs):
    stampedAuth.resetPassword(http_schema.email)

    return transformOutput(True)


def _buildAlertsFromAccount(account):
    alerts = getattr(account, 'alert_settings', None)
    result = []

    def buildToggle(settingType, settingGroup):
        name = 'alerts_%s_%s' % (settingGroup, settingType)
        toggle = HTTPSettingsToggle()
        toggle.toggle_id = name
        toggle.type = settingType
        toggle.value = False
        if alerts is not None and hasattr(alerts, name) and getattr(alerts, name) == True:
            toggle.value = True
        return toggle

    def buildGroup(settingGroup, settingName, alertSuffix):
        group = HTTPSettingsGroup()
        group.group_id = 'alerts_%s' % settingGroup
        group.name = settingName
        group.toggles = [
            buildToggle('apns', settingGroup),
            buildToggle('email', settingGroup),
        ]
        return group

    result.append(buildGroup('followers', 'New Followers', 'follow'))
    result.append(buildGroup('credits', 'Credit', 'credit'))
    result.append(buildGroup('mentions', 'Mentions', 'mention'))
    result.append(buildGroup('comments', 'Comments', 'comment'))
    result.append(buildGroup('replies', 'Replies', 'reply'))
    result.append(buildGroup('likes', 'Likes', 'like'))
    result.append(buildGroup('todos', 'To-Dos', 'todo'))

    return map(lambda x: x.dataExport(), result)


@handleHTTPRequest()
@require_http_methods(["GET"])
def showAlerts(request, authUserId, **kwargs):
    account  = stampedAPI.getAccount(authUserId)
    result = _buildAlertsFromAccount(account)

    return transformOutput(result)


@handleHTTPRequest(http_schema=HTTPSettingsToggleRequest)
@require_http_methods(["POST"])
def updateAlerts(request, authUserId, http_schema, **kwargs):
    on = None
    if http_schema.on is not None:
        on = set(http_schema.on.split(','))

    off = None
    if http_schema.off is not None:
        off = set(http_schema.off.split(','))

    account  = stampedAPI.updateAlerts(authUserId, on, off)
    result = _buildAlertsFromAccount(account)

    return transformOutput(result)


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

