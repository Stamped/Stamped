#!/usr/bin/env python
"""
    Linked account functions
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
from django.http        import HttpResponseRedirect


@handleHTTPRequest(parse_request=False)
@require_http_methods(["GET"])
def show(request, authUserId, **kwargs):
    linkedAccounts = stampedAPI.getLinkedAccounts(authUserId)
    if linkedAccounts is None:
        result = None
    else:
        result = HTTPLinkedAccounts().importLinkedAccounts(linkedAccounts)

    return transformOutput(result.dataExport())

@handleHTTPRequest(http_schema=HTTPLinkedAccount,
                   conversion=HTTPLinkedAccount.exportLinkedAccount)
@require_http_methods(["POST"])
def add(request, authUserId, http_schema, schema, **kwargs):
    result = stampedAPI.addLinkedAccount(authUserId, schema)

    return transformOutput(True)

@handleHTTPRequest(http_schema=HTTPServiceNameForm)
@require_http_methods(["POST"])
def remove(request, authUserId, http_schema, **kwargs):
    result = stampedAPI.removeLinkedAccount(authUserId, http_schema.service_name)

    return transformOutput(True)

@handleHTTPRequest(http_schema=HTTPLinkedAccount)
@require_http_methods(["POST"])
def update(request, authUserId, http_schema, **kwargs):
    result = stampedAPI.updateLinkedAccount(authUserId, http_schema)

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

@handleHTTPRequest(http_schema=HTTPShareSettingsToggleRequest)
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

@handleHTTPRequest(http_schema=HTTPServiceNameForm)
@require_http_methods(["GET"])
def showSettings(request, authUserId, http_schema, **kwargs):
    linked  = stampedAPI.getLinkedAccount(authUserId, http_schema.service_name)
    result = _buildShareSettingsFromLinkedAccount(linked)

    return transformOutput(result)


@handleHTTPRequest()
@require_http_methods(["POST"])
def removeTwitter(request, authUserId, **kwargs):
    result = stampedAPI.removeLinkedAccount(authUserId, 'twitter')

    return transformOutput(True)


@handleHTTPRequest()
@require_http_methods(["POST"])
def removeFacebook(request, authUserId, **kwargs):
    result = stampedAPI.removeLinkedAccount(authUserId, 'facebook')

    return transformOutput(True)

@handleHTTPRequest()
@require_http_methods(["POST"])
def removeTwitter(request, authUserId, **kwargs):
    result = stampedAPI.removeLinkedAccount(authUserId, 'twitter')

    return transformOutput(True)

def createNetflixLoginResponse(request, netflixAddId=None):
    if 'oauth_token' in request.GET:
        oauth_token = request.GET['oauth_token']
    elif 'oauth_token' in request.POST:
        oauth_token = request.POST['oauth_token']
    else:
        raise StampedInputError("Access token not found")


    netflix = globalNetflix()
    secret, url = netflix.getLoginUrl(oauth_token, netflixAddId)

    response                = HTTPEndpointResponse()
    source                  = HTTPActionSource()
    source.source           = 'netflix'
    source.link             = url
    #source.endpoint         = 'account/linked/netflix/login_callback.json'
    response.setAction('netflix_login', 'Login to Netflix', [source])

    return transformOutput(response.dataExport())

@handleHTTPRequest(http_schema=HTTPNetflixId)
@require_http_methods(["GET"])
def netflixLogin(request, authUserId, **kwargs):
    return createNetflixLoginResponse(request, http_schema.netflix_id)

@handleHTTPCallbackRequest(http_schema=HTTPNetflixAuthResponse)
@require_http_methods(["GET"])
def netflixLoginCallback(request, authUserId, http_schema, **kwargs):
    netflix = globalNetflix()
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

@handleHTTPRequest(http_schema=HTTPNetflixId)
@require_http_methods(["POST"])
def addToNetflixInstant(request, authUserId, authClientId, http_schema, **kwargs):
    try:
        result = stampedAPI.addToNetflixInstantWithUserId(authUserId, http_schema.netflix_id)
    except StampedThirdPartyInvalidCredentialsError:
        return createNetflixLoginResponse(request, http_schema.netflix_id)
    if result == None:
        return createNetflixLoginResponse(request, http_schema.netflix_id)

    response = HTTPEndpointResponse()

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


