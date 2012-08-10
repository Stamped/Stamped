#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from schema import Schema
from api.oauthapi import OAuthAPI
from api_old.SchemaValidation import validateString
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
from servers.httpapi.v1.account.errors import account_exceptions
from servers.httpapi.v1.schemas import HTTPUser

# APIs
oauth_api = OAuthAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('old_password', basestring, required=True, cast=validateString)
        cls.addProperty('new_password', basestring, required=True, cast=validateString)

# Set exceptions as list of exceptions 
exceptions = account_exceptions

@require_http_methods(["POST"])
@stamped_http_api_request(form=HTTPForm, 
                            parse_request_kwargs={'obfuscate':['old_password', 'new_password']},
                            exceptions=exceptions)
def run(request, auth_user_id, form, **kwargs):
    oauth_api.verifyPassword(auth_user_id, form.old_password)
    oauth_api.updatePassword(auth_user_id, form.new_password)

    return json_response(True)

