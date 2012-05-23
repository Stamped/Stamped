#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *

@handleHTTPRequest(requires_auth=False, requires_client=True, http_schema=OAuthTokenRequest)
@require_http_methods(["POST"])
def token(request, client_id, http_schema, **kwargs):
    if str(http_schema.grant_type).lower() != 'refresh_token':
        raise StampedHTTPError("invalid_request", 400, "Grant type incorrect")
    
    token = stampedAuth.verifyRefreshToken(client_id, http_schema.refresh_token)
    
    return transformOutput(token)


@handleHTTPRequest(requires_auth=False, requires_client=True, http_schema=OAuthLogin)
@require_http_methods(["POST"])
def login(request, client_id, http_schema, **kwargs):
    account, token = stampedAuth.verifyUserCredentials(client_id, \
                                                    http_schema.login, \
                                                    http_schema.password)
    
    user = HTTPUser().importAccount(account)
    logs.user(user.user_id)
    
    output = { 'user' : user.dataExport(), 'token' : token }
    
    return transformOutput(output)

@handleHTTPRequest(requires_auth=False, requires_client=True, http_schema=OAuthFacebookLogin)
@require_http_methods(["POST"])
def loginWithFacebook(request, client_id, http_schema, **kwargs):
    account, token = stampedAuth.verifyFacebookUserCredentials(client_id, http_schema.fb_token)

    user = HTTPUser().importAccount(account)
    logs.user(user.user_id)

    output = { 'user' : user.dataExport(), 'token' : token }

    return transformOutput(output)