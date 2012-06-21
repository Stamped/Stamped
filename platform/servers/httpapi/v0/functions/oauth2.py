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
        raise StampedInputError("Grant type incorrect")
    
    token = stampedAuth.verifyRefreshToken(client_id, http_schema.refresh_token)
    
    return transformOutput(token)


@handleHTTPRequest(requires_auth=False, requires_client=True, http_schema=OAuthLogin)
@require_http_methods(["POST"])
def login(request, client_id, http_schema, **kwargs):
    try:
        account, token = stampedAuth.verifyUserCredentials(client_id, http_schema.login, http_schema.password)
    except StampedInvalidCredentialsError:
        raise StampedHTTPError(409, kind="invalid_credentials")
    
    user = HTTPUser().importAccount(account)
    logs.user(user.user_id)
    
    output = { 'user' : user.dataExport(), 'token' : token }
    
    return transformOutput(output)

@handleHTTPRequest(requires_auth=False, requires_client=True, http_schema=OAuthFacebookLogin)
@require_http_methods(["POST"])
def loginWithFacebook(request, client_id, http_schema, **kwargs):
    try:
        account, token = stampedAuth.verifyFacebookUserCredentials(client_id, http_schema.user_token)
    except (StampedInputError, StampedInvalidCredentialsError):
        raise StampedHTTPError(400, msg="Facebook login failed")
    except StampedLinkedAccountExistsError:
        raise StampedHTTPError(409, msg="Multiple accounts exist for this Facebook user")

    user = HTTPUser().importAccount(account)
    logs.user(user.user_id)

    output = { 'user' : user.dataExport(), 'token' : token }

    return transformOutput(output)

@handleHTTPRequest(requires_auth=False, requires_client=True, http_schema=OAuthTwitterLogin)
@require_http_methods(["POST"])
def loginWithTwitter(request, client_id, http_schema, **kwargs):
    try:
        account, token = stampedAuth.verifyTwitterUserCredentials(client_id, http_schema.user_token, http_schema.user_secret)
    except (StampedInputError, StampedInvalidCredentialsError):
        raise StampedHTTPError(400, msg="Twitter login failed")
    except StampedLinkedAccountExistsError:
        raise StampedHTTPError(409, msg="Multiple accounts exist for this Twitter user")

    user = HTTPUser().importAccount(account)
    logs.user(user.user_id)

    output = { 'user' : user.dataExport(), 'token' : token }

    return transformOutput(output)