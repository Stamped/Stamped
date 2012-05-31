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


@handleHTTPRequest(parse_request=False)
@require_http_methods(["GET"])
def show(request, authUserId, **kwargs):
    linkedAccounts = stampedAPI.getLinkedAccounts(authUserId)
    logs.info('### linkedAccounts %s' % linkedAccounts)
    if linkedAccounts is None:
        result = None
    else:
        result = HTTPLinkedAccounts().importLinkedAccounts(linkedAccounts)

    return transformOutput(result.dataExport())

@handleHTTPRequest(http_schema=HTTPLinkedAccount)
@require_http_methods(["POST"])
def add(request, authUserId, http_schema, **kwargs):
    if http_schema.service_name == 'facebook':
        pass
    elif http_schema.service_name == 'twitter':
        pass
    elif http_schema.service_name == 'netflix':
        pass

    linkedAccount = http_schema.exportLinkedAccount()
    logs.info('### linkedAccount: %s' % linkedAccount)
    result = stampedAPI.addLinkedAccount(authUserId, linkedAccount)

    return transformOutput(result)

@handleHTTPRequest(http_schema=HTTPRemoveLinkedAccountForm)
@require_http_methods(["POST"])
def remove(request, authUserId, http_schema, **kwargs):
    result = stampedAPI.removeLinkedAccount(authUserId, http_schema.service_name)

    return transformOutput(True)



@handleHTTPRequest(http_schema=HTTPLinkedAccounts)
@require_http_methods(["POST"])
def linked_accounts(request, authUserId, http_schema, **kwargs):
    linked          = http_schema.exportLinkedAccounts()
    twitterAuth     = http_schema.exportTwitterAuthSchema()
    facebookAuth    = http_schema.exportFacebookAuthSchema()
    netflixAuth     = http_schema.exportNetflixAuthSchema()

    data = {
        'twitter'       : linked.twitter,
        'facebook'      : linked.facebook,
        'twitterAuth'   : twitterAuth,
        'facebookAuth'  : facebookAuth,
        'netflixAuth'   : netflixAuth,
        }
    stampedAPI.updateLinkedAccounts(authUserId, **data)

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

def createNetflixLoginResponse(authUserId):
    netflix = globalNetflix()
    secret, url = netflix.getLoginUrl(authUserId)

    response                = HTTPEndpointResponse()
    source                  = HTTPActionSource()
    source.source           = 'netflix'
    source.link             = url
    #source.endpoint         = 'https://dev.stamped.com/v0/account/linked/netflix/login_callback.json'
    response.setAction('netflix_login', 'Login to Netflix', [source])

    return transformOutput(response.dataExport())

@handleHTTPRequest()
@require_http_methods(["GET"])
def netflixLogin(request, authUserId, http_schema, **kwargs):
    return createNetflixLoginResponse(authUserId)

@handleHTTPRequest(requires_auth=False, http_schema=HTTPNetflixAuthResponse,
    parse_request_kwargs={'allow_oauth_token': True})
@require_http_methods(["GET"])
def netflixLoginCallback(request, authUserId, http_schema, **kwargs):
    netflix = globalNetflix()

    result = netflix.requestUserAuth(http_schema.oauth_token, http_schema.secret)

    netflixAuth = NetflixAuthSchema()
    netflixAuth.netflix_token       = result['oauth_token']
    netflixAuth.netflix_secret      = result['oauth_token_secret']
    netflixAuth.netflix_user_id     = result['user_id']

    stampedAPI.updateLinkedAccounts(http_schema.stamped_oauth_token, netflixAuth=netflixAuth)

    return createNetflixLoginResponse(authUserId)




@handleHTTPRequest(http_schema=HTTPNetflixId)
@require_http_methods(["POST"])
def addToNetflixInstant(request, authUserId, http_schema, **kwargs):
    logs.info('adding to netflix instant id: %s' % http_schema.netflix_id)
    try:
        result = stampedAPI.addToNetflixInstant(authUserId, http_schema.netflix_id)
    except StampedHTTPError as e:
        if e.code == 401:
            return createNetflixLoginResponse(authUserId)
            # return login endpoint action
        else:
            raise e
    if result == None:
        return createNetflixLoginResponse(authUserId)

    response = HTTPEndpointResponse()

    source                  = HTTPActionSource()
    source.source           = 'stamped_confirm'
    source.source_data      = 'The item is now added to your Netflix Queue.'
    #source.endpoint         = 'https://dev.stamped.com/v0/account/linked/netflix/login_callback.json'
    response.setAction('netflix_login', 'Login to Netflix', [source])
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

