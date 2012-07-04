#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *


exceptions = [
    (StampedInvalidAuthTokenError,          StampedHTTPError(401, kind='invalid_credentials', msg="Invalid Access Token")),
    (StampedInvalidRefreshTokenError,       StampedHTTPError(401, kind='invalid_credentials', msg="Invalid Refresh Token")),
    (StampedInvalidClientError,             StampedHTTPError(401, kind='invalid_credentials', msg="Invalid client credentials")),
    (StampedGrantTypeIncorrectError,        StampedHTTPError(400, kind='bad_request', msg="There was a problem authorizing the account")),
    (StampedAccountNotFoundError,           StampedHTTPError(401, kind='invalid_credentials', msg='The username / password combination was incorrect')),
    (StampedInvalidCredentialsError,        StampedHTTPError(401, kind='invalid_credentials', msg="The username / password combination was incorrect")),
]

@handleHTTPRequest(requires_auth=False,
                   requires_client=True,
                   http_schema=OAuthTokenRequest,
                   exceptions=exceptions)
@require_http_methods(["POST"])
def token(request, client_id, http_schema, **kwargs):
    if str(http_schema.grant_type).lower() != 'refresh_token':
        raise StampedGrantTypeIncorrectError("Grant type incorrect")
    
    token = stampedAuth.verifyRefreshToken(client_id, http_schema.refresh_token)
    
    return transformOutput(token)


exceptions_login = [
    (StampedWrongAuthServiceError,          StampedHTTPError(401, kind='invalid_credentials', msg="This account does uses a third-party service for authentication")),
]
@handleHTTPRequest(requires_auth=False,
                   requires_client=True,
                   http_schema=OAuthLogin,
                   exceptions=exceptions + exceptions_login)
@require_http_methods(["POST"])
def login(request, client_id, http_schema, **kwargs):
    account, token = stampedAuth.verifyUserCredentials(client_id, http_schema.login, http_schema.password)
    
    user = HTTPUser().importAccount(account)
    logs.user(user.user_id)
    
    output = { 'user' : user.dataExport(), 'token' : token }
    
    return transformOutput(output)

exceptions_loginWithFacebook = [
    (StampedLinkedAccountAlreadyExistsError, StampedHTTPError(409, kind='bad_request', msg="Sorry, the Facebook account is linked to multiple Stamped accounts")),
    (StampedThirdPartyError,                 StampedHTTPError(401, kind='invalid_credentials', msg="Facebook login failed")),
    (StampedWrongAuthServiceError,           StampedHTTPError(401, kind='invalid_credentials', msg="Account does not use Facebook authentication")),
]
@handleHTTPRequest(requires_auth=False,
                   requires_client=True,
                   http_schema=OAuthFacebookLogin,
                   exceptions=exceptions + exceptions_loginWithFacebook,)
@require_http_methods(["POST"])
def loginWithFacebook(request, client_id, http_schema, **kwargs):
    account, token = stampedAuth.verifyFacebookUserCredentials(client_id, http_schema.user_token)

    user = HTTPUser().importAccount(account)
    logs.user(user.user_id)

    output = { 'user' : user.dataExport(), 'token' : token }

    return transformOutput(output)

exceptions_loginWithTwitter = [
    (StampedLinkedAccountAlreadyExistsError, StampedHTTPError(401, kind='bad_request', msg="Sorry, the Facebook account is linked to multiple Twitter accounts")),
    (StampedThirdPartyError,                 StampedHTTPError(401, kind='invalid_credentials', msg="Twitter login failed")),
    (StampedWrongAuthServiceError,           StampedHTTPError(401, kind='invalid_credentials', msg="Account does not use Facebook authentication")),
]
@handleHTTPRequest(requires_auth=False,
                   requires_client=True,
                   http_schema=OAuthTwitterLogin,
                   exceptions=exceptions + exceptions_loginWithTwitter)
@require_http_methods(["POST"])
def loginWithTwitter(request, client_id, http_schema, **kwargs):
    account, token = stampedAuth.verifyTwitterUserCredentials(client_id, http_schema.user_token, http_schema.user_secret)

    user = HTTPUser().importAccount(account)
    logs.user(user.user_id)

    output = { 'user' : user.dataExport(), 'token' : token }

    return transformOutput(output)