#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import logs

from errors import StampedWrongAuthServiceError
from schema import Schema
from api_old.SchemaValidation import validateString
from api.oauthapi import OAuthAPI
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
from servers.httpapi.v1.schemas import HTTPUser
from servers.httpapi.v1.oauth2.errors import oauth_exceptions

# APIs
oauth_api = OAuthAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('login', basestring, required=True)
        cls.addProperty('password', basestring, required=True, cast=validateString)

# Set exceptions as list of exceptions 
exceptions = [
    (StampedWrongAuthServiceError, 401, 'invalid_credentials', "This account does uses a third-party service for authentication"),
] + oauth_exceptions

@require_http_methods(["POST"])
@stamped_http_api_request(requires_auth=False, requires_client=True, form=HTTPForm, exceptions=exceptions)
def run(request, client_id, form, **kwargs):
    account, token = oauth_api.verifyUserCredentials(client_id, form.login, form.password)

    user = HTTPUser().importAccount(account)
    logs.user(user.user_id)

    result = {'user': user.data_export(), 'token': token}

    return json_response(result)

