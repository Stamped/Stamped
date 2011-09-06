#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from httpapi.v0.helpers import *

@handleHTTPRequest
@require_http_methods(["POST"])
def token(request):
    client_id   = checkClient(request)
    schema      = parseRequest(OAuthTokenRequest(), request)

    if str(schema.grant_type).lower() != 'refresh_token':
        msg = "Grant type incorrect"
        logs.warning(msg)
        raise StampedHTTPError("invalid_request", 400, msg)

    token       = stampedAuth.verifyRefreshToken(client_id, schema.refresh_token)
    
    return transformOutput(token)


@handleHTTPRequest
@require_http_methods(["POST"])
def login(request):
    client_id   = checkClient(request)
    schema      = parseRequest(OAuthLogin(), request)

    token       = stampedAuth.verifyUserCredentials(client_id, \
                                                    schema.login, \
                                                    schema.password)

    return transformOutput(token)


