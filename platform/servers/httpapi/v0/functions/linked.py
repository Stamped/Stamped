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

@handleHTTPRequest(http_schema=HTTPLinkedAccount)
@require_http_methods(["POST"])
def add(request, authUserId, http_schema, **kwargs):
    linkedAccount = http_schema.exportLinkedAccount()
    result = stampedAPI.addLinkedAccount(authUserId, linkedAccount)

    return transformOutput(True)

@handleHTTPRequest(http_schema=HTTPRemoveLinkedAccountForm)
@require_http_methods(["POST"])
def remove(request, authUserId, http_schema, **kwargs):
    result = stampedAPI.removeLinkedAccount(authUserId, http_schema.service_name)

    return transformOutput(True)

@handleHTTPRequest(http_schema=HTTPLinkedAccount)
@require_http_methods(["POST"])
def update(request, authUserId, http_schema, **kwargs):
    result = stampedAPI.updateLinkedAccount(authUserId, http_schema)

    return transformOutput(True)

@handleHTTPRequest(http_schema=HTTPUpdateLinkedAccountShareSettingsForm,
                   conversion=HTTPUpdateLinkedAccountShareSettingsForm.exportLinkedAccountShareSettings)
@require_http_methods(["POST"])
def updateShareSettings(request, authUserId, http_schema, schema, **kwargs):
    result = stampedAPI.updateLinkedAccountShareSettings(authUserId, http_schema.service_name, schema)
    return transformOutput(True)


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

    logs.info('### netflixLoginCallback result: %s' % result)

    linked                          = LinkedAccount()
    linked.service_name             = 'netflix'
    linked.linked_user_id           = result['user_id']
    linked.token                    = result['oauth_token']
    linked.secret                   = result['oauth_token_secret']
    stampedAPI.addLinkedAccount(authUserId, linked)

    if http_schema.netflix_add_id is not None:
        try:
            logs.info('### authUserId: %s' % authUserId)
            result = stampedAPI.addToNetflixInstant(authUserId, http_schema.netflix_id)
        except Exception as e:
            return HttpResponseRedirect("stamped://netflix/add/fail")
        if result == None:
            return HttpResponseRedirect("stamped://netflix/add/fail")
        return HttpResponseRedirect("stamped://netflix/add/success")
    return HttpResponseRedirect("stamped://netflix/link/success")

@handleHTTPRequest(http_schema=HTTPNetflixId)
@require_http_methods(["POST"])
def addToNetflixInstant(request, authUserId, authClientId, http_schema, **kwargs):
    try:
        result = stampedAPI.addToNetflixInstant(authUserId, http_schema.netflix_id)
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


