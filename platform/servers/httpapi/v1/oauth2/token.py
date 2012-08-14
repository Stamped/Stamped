#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from errors import StampedGrantTypeIncorrectError
from schema import Schema
from api.oauthapi import OAuthAPI
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
from servers.httpapi.v1.oauth2.errors import oauth_exceptions

# APIs
oauth_api = OAuthAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('refresh_token', basestring, required=True)
        cls.addProperty('grant_type', basestring, required=True)

# Set exceptions as list of exceptions 
exceptions = oauth_exceptions

@require_http_methods(["POST"])
@stamped_http_api_request(requires_auth=False, requires_client=True, form=HTTPForm, exceptions=exceptions)
def run(request, client_id, form, **kwargs):
    if form.grant_type.lower() != 'refresh_token':
        raise StampedGrantTypeIncorrectError("Grant type incorrect")

    token = oauth_api.verifyRefreshToken(client_id, form.refresh_token)

    ### RESTRUCTURE TODO: Verify token is proper format
    result = token

    return json_response(result)

