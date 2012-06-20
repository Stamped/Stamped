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
    logs.info('### %s' % linkedAccounts)
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
    result = stampedAPI.updateLinkedAccount(authUserId, http_schema.service_name)

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

def createNetflixLoginResponse(authUserId, netflixAddId=None):
    netflix = globalNetflix()
    secret, url = netflix.getLoginUrl(authUserId, netflixAddId)

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
    return createNetflixLoginResponse(authUserId, http_schema.netflix_id)

@handleHTTPRequest(requires_auth=False, http_schema=HTTPNetflixAuthResponse,
    parse_request_kwargs={'allow_oauth_token': True})
@require_http_methods(["GET"])
def netflixLoginCallback(request, authUserId, http_schema, **kwargs):
    netflix = globalNetflix()
    authUserId = http_schema.stamped_oauth_token
    # Acquire the user's final oauth_token/secret pair and add the netflix linked account
    try:
        result = netflix.requestUserAuth(http_schema.oauth_token, http_schema.secret)
    except Exception as e:
        return HttpResponseRedirect("stamped://netflix/link/fail")
    linked                          = LinkedAccount()
    linked.service_name             = 'netflix'
    linked.user_id                  = result['user_id']
    linked.token                    = result['oauth_token']
    linked.secret                   = result['oauth_token_secret']
    stampedAPI.addLinkedAccount(authUserId, linked)

    if http_schema.netflix_add_id is not None:
        try:
            result = stampedAPI.addToNetflixInstant(authUserId, http_schema.netflix_id)
        except StampedHTTPError as e:
            return HttpResponseRedirect("stamped://netflix/add/fail")
        if result == None:
            return HttpResponseRedirect("stamped://netflix/add/fail")
        return HttpResponseRedirect("stamped://netflix/add/success")
    return HttpResponseRedirect("stamped://netflix/link/success")

@handleHTTPRequest(http_schema=HTTPNetflixId)
@require_http_methods(["POST"])
def addToNetflixInstant(request, authUserId, http_schema, **kwargs):
    try:
        result = stampedAPI.addToNetflixInstant(authUserId, http_schema.netflix_id)
    except StampedHTTPError as e:
        if e.code == 401:
            return createNetflixLoginResponse(authUserId, http_schema.netflix_id)
            # return login endpoint action
        else:
            raise e
    if result == None:
        return createNetflixLoginResponse(authUserId, http_schema.netflix_id)

    response = HTTPEndpointResponse()

    source                              = HTTPActionSource()
    source.name                         = 'Added to Netflix Instant Queue'
    source.source                       = 'stamped'
    source.source_data                  = dict()
    source.source_data['title']         = 'Added to Netflix Instant Queue'
    source.source_data['subtitle']      = 'Instant Queue'
    source.source_data['icon']          = 'http://static.stamped.com/assets/icons/default/src_netflix.png'
    #source.endpoint         = 'account/linked/netflix/login_callback.json'
    response.setAction('stamped_confirm', 'Added to Netflix', [source])
    #TODO throw status codes on error
    #TODO return an HTTPAction
    return transformOutput(response.dataExport())

@handleHTTPRequest(http_schema=HTTPNetflixId)
@require_http_methods(["POST"])
def removeFromNetflixInstant(request, authUserId, http_schema, **kwargs):
    try:
        result = stampedAPI.addToNetflixQueue(authUserId, http_schema.netflix_id)
    except StampedHTTPError as e:
        if e.code == 401:
            #redirect to sign in
            raise e
        else:
            raise e
        #TODO throw status codes on error
    #TODO return an HTTPAction
    return transformOutput(True)

