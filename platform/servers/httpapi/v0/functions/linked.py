#!/usr/bin/env python
from __future__ import absolute_import
"""
    Linked account functions
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import time
from datetime import datetime
from servers.httpapi.v0.helpers import *
from errors             import *
from api.HTTPSchemas        import *
from libs.Netflix       import *
from libs.Facebook           import *
from django.http        import HttpResponseRedirect


exceptions = [
    (StampedAccountNotFoundError, 404, 'not_found', 'There was an error retrieving account information'),
    (StampedMissingLinkedAccountTokenError, 400, 'invalid_credentials', "Must provide a token for third party service"),
    (StampedNetflixNoInstantWatchError, 403, 'illegal_action', "Netflix account must have instant watch access"),
    (StampedLinkedAccountDoesNotExistError, 400, 'illegal_action', "No such third party account linked to user"),
    (StampedLinkedAccountIsAuthError, 403, 'forbidden', "This third-party account is used for authorization and cannot be removed"),
    (StampedLinkedAccountAlreadyExistsError, 409, 'invalid_credentials', "Another user is already connected to this third-party account"),
    (StampedThirdPartyError, 403, 'illegal_action', "There was a problem communicating with the third-party service"),
    (StampedLinkedAccountMismatchError, 400, 'illegal_action', "There was a problem verifying the third-party account"),
    (StampedFacebookTokenError, 401, 'facebook_auth', "Facebook login failed. Please reauthorize your account."),
]

@handleHTTPRequest(parse_request=False,
                   exceptions=exceptions)
@require_http_methods(["GET"])
def show(request, authUserId, **kwargs):
    linkedAccounts = stampedAPI.getLinkedAccounts(authUserId)

    if linkedAccounts is None:
        result = {}
    else:
        result = HTTPLinkedAccounts().importLinkedAccounts(linkedAccounts).dataExport()

    return transformOutput(result)

@handleHTTPRequest(http_schema=HTTPLinkedAccount,
                   conversion=HTTPLinkedAccount.exportLinkedAccount,
                   exceptions=exceptions)
@require_http_methods(["POST"])
def add(request, authUserId, http_schema, schema, **kwargs):
    if http_schema.service_name is None:
        if 'service_name' not in kwargs:
            raise StampedMissingParametersError("Missing linked account service_name parameter")
        else:
            schema.service_name = kwargs['service_name']

    # Quick fix to prevent share settings from being overwritten
    acct = stampedAPI.getAccount(authUserId)
    if schema.service_name == 'facebook':
        if acct.linked is not None and acct.linked.facebook is not None:
            schema.share_settings = acct.linked.facebook.share_settings
    result = stampedAPI.addLinkedAccount(authUserId, schema)

    return transformOutput(True)

@handleHTTPRequest(http_schema=HTTPServiceNameForm,
                   exceptions=exceptions)
@require_http_methods(["POST"])
def remove(request, authUserId, http_schema, **kwargs):
    if http_schema.service_name is None:
        if 'service_name' not in kwargs:
            raise StampedMissingParametersError("Missing Linked account service_name parameter")
        else:
            http_schema.service_name = kwargs['service_name']

    result = stampedAPI.removeLinkedAccount(authUserId, http_schema.service_name)

    return transformOutput(True)

def _buildShareSettingsFromLinkedAccount(linked):
    shares = getattr(linked, 'share_settings', None)
    result = []

    def buildToggle(settingType):
        name = 'share_%s' % settingType
        toggle = HTTPSettingsToggle()
        toggle.toggle_id = name
        toggle.type = settingType
        toggle.value = False
        if shares is not None and hasattr(shares, name) and getattr(shares, name) == True:
            toggle.value = True
        return toggle

    def buildGroup(settingGroup, settingName):
        group = HTTPSettingsGroup()
        group.group_id = 'share_%s' % settingGroup
        group.name = settingName
        group.toggles = [
            buildToggle(settingGroup)
        ]
        return group

    result.append(buildGroup('stamps', 'Publish My Stamps'))
    result.append(buildGroup('likes', 'Publish Stamps That I Like'))
    result.append(buildGroup('todos', "Publish My Todo's"))
    result.append(buildGroup('follows', "Publish When I Follow Someone"))

    return map(lambda x: x.dataExport(), result)

@handleHTTPRequest(http_schema=HTTPShareSettingsToggleRequest,
                   exceptions=exceptions)
@require_http_methods(["POST"])
def updateSettings(request, authUserId, http_schema, **kwargs):
    on = None
    if http_schema.on is not None:
        on = set(http_schema.on.split(','))

    off = None
    if http_schema.off is not None:
        off = set(http_schema.off.split(','))

    logs.info('### on: %s' % on)
    linkedAccount  = stampedAPI.updateLinkedAccountShareSettings(authUserId, http_schema.service_name, on, off)
    result = _buildShareSettingsFromLinkedAccount(linkedAccount)

    return transformOutput(result)

@handleHTTPRequest(http_schema=HTTPServiceNameForm,
                   exceptions=exceptions)
@require_http_methods(["GET"])
def showSettings(request, authUserId, http_schema, **kwargs):
    linked  = stampedAPI.getLinkedAccount(authUserId, http_schema.service_name)
    result = _buildShareSettingsFromLinkedAccount(linked)

    return transformOutput(result)

def createNetflixLoginResponse(request, netflixAddId=None):
    if 'oauth_token' in request.GET:
        oauth_token = request.GET['oauth_token']
    elif 'oauth_token' in request.POST:
        oauth_token = request.POST['oauth_token']
    else:
        raise StampedMissingLinkedAccountTokenError("Access token not found")


    netflix = globalNetflix()
    secret, url = netflix.getLoginUrl(oauth_token, netflixAddId)

    response                = HTTPActionResponse()
    source                  = HTTPActionSource()
    source.source           = 'netflix'
    source.link             = url
    #source.endpoint         = 'account/linked/netflix/login_callback.json'
    response.setAction('netflix_login', 'Login to Netflix', [source])

    print ('### netflix login response: %s' % response.dataExport())

    return transformOutput(response.dataExport())

@handleHTTPRequest(http_schema=HTTPNetflixId,
                   exceptions=exceptions)
@require_http_methods(["GET"])
def netflixLogin(request, http_schema, authUserId, **kwargs):
    return createNetflixLoginResponse(request, http_schema.netflix_id)

@handleHTTPCallbackRequest(http_schema=HTTPNetflixAuthResponse,
                           exceptions=exceptions)
@require_http_methods(["GET"])
def netflixLoginCallback(request, authUserId, http_schema, **kwargs):
    netflix = globalNetflix()

    logs.info('### http_schema: %s ' % http_schema)

    # Acquire the user's final oauth_token/secret pair and add the netflix linked account
    try:
        result = netflix.requestUserAuth(http_schema.oauth_token, http_schema.secret)
    except Exception as e:
        return HttpResponseRedirect("stamped://netflix/link/fail")



    linked                          = LinkedAccount()
    linked.service_name             = 'netflix'
    linked.linked_user_id           = result['user_id']
    linked.token                    = result['oauth_token']
    linked.secret                   = result['oauth_token_secret']
    stampedAPI.addLinkedAccount(authUserId, linked)

    if http_schema.netflix_add_id is not None:
        try:
            result = stampedAPI.addToNetflixInstant(linked.linked_user_id, linked.token, linked.secret, http_schema.netflix_add_id)
        except Exception as e:
            logs.warning('Error adding to netflix: %s' % e)
            return HttpResponseRedirect("stamped://netflix/add/fail")
        if result == None:
            logs.warning('Error adding to netflix.  Returned no result.')
            return HttpResponseRedirect("stamped://netflix/add/fail")
        return HttpResponseRedirect("stamped://netflix/add/success")
    return HttpResponseRedirect("stamped://netflix/link/success")


def createFacebookLoginResponse(authUserId):
    logs.info('called createFacebookLoginResponse with user_id: %s' % authUserId)
    facebook = stampedAPI._facebook
    oid = stampedAPI._fbCallbackTokenDB.addUserId(authUserId)
    url = facebook.getLoginUrl(authUserId, oid)

    logs.info('url: %s' % url)

    response                = HTTPActionResponse()
    source                  = HTTPActionSource()
    source.source           = 'facebook'
    source.link             = url
    response.setAction('facebook_login', 'Login to Facebook', [source])

    print ('### Facebook login response: %s' % response.dataExport())
    return transformOutput(response.dataExport())



@handleHTTPRequest(exceptions=exceptions)
@require_http_methods(["POST"])
def facebookLogin(request, authUserId, **kwargs):
    result =  createFacebookLoginResponse(authUserId)
    logs.info('result: %s' % result)
    return result


@handleHTTPCallbackRequest(requires_auth=False,
                           http_schema=HTTPFacebookAuthResponse,
                           exceptions=exceptions)
@require_http_methods(["GET"])
def facebookLoginCallback(request, http_schema, **kwargs):
    facebook = globalFacebook()

    logs.info('### http_schema: %s ' % http_schema)

    oid = http_schema.state
    authUserId = stampedAPI._fbCallbackTokenDB.getUserId(oid)
    #stampedAPI._fbCallbackTokenDB.removeUserId(oid)
#    authUserId, client_id = checkOAuth(oauth_token)
    # Acquire the user's FB access token
    try:
        access_token, expires = facebook.getUserAccessToken(http_schema.code)
        logs.info('### FIRST: token: %s  expires: %s' % (access_token, expires))

        access_token, expires = facebook.extendAccessToken(access_token)
        logs.info('### SECOND: token: %s  expires: %s' % (access_token, expires))
    except Exception as e:
        return HttpResponseRedirect("stamped://facebook/link/fail")

    acct = stampedAPI.getAccount(authUserId)


    expires_dt = datetime.fromtimestamp(time.time() + expires)
    # If the user already has a FB account, then update it with the new access_token
    if acct.linked is not None and acct.linked.facebook is not None:
        linked = acct.linked.facebook
        linked.token = access_token
        linked.token_expiration = expires_dt
        linked.extended_timestamp = datetime.utcnow()

        linked.share_settings = LinkedAccountShareSettings()
        linked.share_settings.share_stamps  = True
        linked.share_settings.share_likes   = True
        linked.share_settings.share_todos   = True
        linked.share_settings.share_follows = True

        stampedAPI._accountDB.updateLinkedAccount(authUserId, linked)
    # Otherwise, we'll get the User's info with the access token and create a new linked account
    else:
        userInfo = facebook.getUserInfo(access_token)
        linked                          = LinkedAccount()
        linked.service_name             = 'facebook'
        linked.token                    = access_token
        linked.token_expiration         = expires_dt
        linked.extended_timestamp       = datetime.utcnow()
        linked.linked_user_id           = userInfo['id']
        linked.linked_screen_name       = userInfo.get('username', None)
        linked.linked_name              = userInfo['name']
        linked.third_party_id           = userInfo['third_party_id']

        linked.share_settings = LinkedAccountShareSettings()
        linked.share_settings.share_stamps  = True
        linked.share_settings.share_likes   = True
        linked.share_settings.share_todos   = True
        linked.share_settings.share_follows = True

        stampedAPI.addLinkedAccount(authUserId, linked)

    #return HttpResponseRedirect("stamped://facebook/link/success")
    url = "fb297022226980395://authorize/#access_token=%s&expires_in=%s&code=%s" % (access_token, expires, http_schema.code)
    return HttpResponseRedirect(url)


@handleHTTPRequest(http_schema=HTTPNetflixId,
                   exceptions=exceptions)
@require_http_methods(["POST"])
def addToNetflixInstant(request, authUserId, authClientId, http_schema, **kwargs):
    try:
        result = stampedAPI.addToNetflixInstantWithUserId(authUserId, http_schema.netflix_id)
    except StampedThirdPartyInvalidCredentialsError:
        return createNetflixLoginResponse(request, http_schema.netflix_id)
    if result == None:
        return createNetflixLoginResponse(request, http_schema.netflix_id)

    response = HTTPActionResponse()

    source                              = HTTPActionSource()
    source.name                         = 'Added to Netflix Instant Queue'
    source.source                       = 'stamped'
    source.source_data                  = dict()
    source.source_data['title']         = 'Added to Netflix'
    source.source_data['subtitle']      = 'Instant Queue'
    source.setIcon('act_response_netflix', stampedAuth.getClientDetails(authClientId))
    #source.endpoint         = 'account/linked/netflix/login_callback.json'
    response.setAction('stamped_confirm', 'Added to Netflix', [source])
    #TODO throw status codes on error
    #TODO return an HTTPAction
    return transformOutput(response.dataExport())
