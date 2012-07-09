#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from servers.httpapi.v0.helpers import *

defaultExceptions = [
    (StampedInvalidAuthTokenError,              401, 'invalid_token', None),
    (StampedInvalidRefreshTokenError,           401, 'invalid_token', None),
    (StampedInvalidClientError,                 401, 'invalid_client', None),
    (StampedGrantTypeIncorrectError,            400, 'invalid_grant', None),
    (StampedAccountNotFoundError,               401, 'invalid_credentials',  "The username / password combination is incorrect"),
    (StampedInvalidCredentialsError,            401, 'invalid_credentials',  "The username / password combination is incorrect"),
]

loginExceptions = [
    (StampedWrongAuthServiceError,              401, 'invalid_credentials', "This account does uses a third-party service for authentication"),
] + defaultExceptions

facebookExceptions = [
    (StampedLinkedAccountAlreadyExistsError,    409, 'bad_request', "The Facebook account is linked to multiple Stamped accounts"),
    (StampedThirdPartyError,                    401, 'invalid_credentials', "Facebook login failed"),
    (StampedWrongAuthServiceError,              400, 'invalid_request', "Account does not use Facebook authentication"),
] + defaultExceptions

twitterExceptions = [
    (StampedLinkedAccountAlreadyExistsError,    409, 'bad_request', "The Twitter account is linked to multiple Stamped accounts"),
    (StampedThirdPartyError,                    401, 'invalid_credentials', "Twitter login failed"),
    (StampedWrongAuthServiceError,              400, 'invalid_request', "Account does not use Twitter authentication"),
] + defaultExceptions


@require_http_methods(["POST"])
@handleHTTPRequest(requires_auth=False,
                   requires_client=True,
                   http_schema=OAuthTokenRequest,
                   exceptions=defaultExceptions)
def token(request, client_id, http_schema, **kwargs):
    if str(http_schema.grant_type).lower() != 'refresh_token':
        raise StampedGrantTypeIncorrectError("Grant type incorrect")
    
    token = stampedAuth.verifyRefreshToken(client_id, http_schema.refresh_token)
    
    return transformOutput(token)


@require_http_methods(["POST"])
@handleHTTPRequest(requires_auth=False,
                   requires_client=True,
                   http_schema=OAuthLogin,
                   exceptions=loginExceptions)
def login(request, client_id, http_schema, **kwargs):
    account, token = stampedAuth.verifyUserCredentials(client_id, http_schema.login, http_schema.password)
    
    user = HTTPUser().importAccount(account)
    logs.user(user.user_id)
    
    output = { 'user' : user.dataExport(), 'token' : token }
    
    return transformOutput(output)


@require_http_methods(["POST"])
@handleHTTPRequest(requires_auth=False,
                   requires_client=True,
                   http_schema=OAuthFacebookLogin,
                   exceptions=facebookExceptions)
def loginWithFacebook(request, client_id, http_schema, **kwargs):
    account, token = stampedAuth.verifyFacebookUserCredentials(client_id, http_schema.user_token)

    user = HTTPUser().importAccount(account)
    logs.user(user.user_id)

    output = { 'user' : user.dataExport(), 'token' : token }

    return transformOutput(output)


@require_http_methods(["POST"])
@handleHTTPRequest(requires_auth=False,
                   requires_client=True,
                   http_schema=OAuthTwitterLogin,
                   exceptions=twitterExceptions)
def loginWithTwitter(request, client_id, http_schema, **kwargs):
    account, token = stampedAuth.verifyTwitterUserCredentials(client_id, http_schema.user_token, http_schema.user_secret)

    user = HTTPUser().importAccount(account)
    logs.user(user.user_id)

    output = { 'user' : user.dataExport(), 'token' : token }

    return transformOutput(output)