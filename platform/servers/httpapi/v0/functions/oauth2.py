#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from servers.httpapi.v0.helpers import *


exceptions = [
    (StampedInvalidAuthTokenError,          401, 'invalid_credentials', "Invalid Access Token"),
    (StampedInvalidRefreshTokenError,       401, 'invalid_credentials', "Invalid Refresh Token"),
    (StampedInvalidClientError,             401, 'invalid_credentials', "Invalid client credentials"),
    (StampedGrantTypeIncorrectError,        400, 'bad_request', "There was a problem authorizing the account"),
    (StampedAccountNotFoundError,           401, 'invalid_credentials', 'The username / password combination was incorrect'),
    (StampedInvalidCredentialsError,        401, 'invalid_credentials', "The username / password combination was incorrect"),
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
    (StampedWrongAuthServiceError,          401, 'invalid_credentials', "This account does uses a third-party service for authentication"),
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
    (StampedLinkedAccountAlreadyExistsError, 409, 'bad_request', "Sorry, the Facebook account is linked to multiple Stamped accounts"),
    (StampedThirdPartyError,                 401, 'invalid_credentials', "Facebook login failed"),
    (StampedWrongAuthServiceError,           401, 'invalid_credentials', "Account does not use Facebook authentication"),
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
    (StampedLinkedAccountAlreadyExistsError, 401, 'bad_request', "Sorry, the Facebook account is linked to multiple Twitter accounts"),
    (StampedThirdPartyError,                 401, 'invalid_credentials', "Twitter login failed"),
    (StampedWrongAuthServiceError,           401, 'invalid_credentials', "Account does not use Facebook authentication"),
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