#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from schema import Schema
from api.accountapi import AccountAPI
from api_old.SchemaValidation import validateHexColor
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
from servers.httpapi.v1.accounts.errors import account_exceptions
from servers.httpapi.v1.schemas import HTTPUser

# APIs
account_api = AccountAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('color_primary', basestring, required=True, cast=validateHexColor)
        cls.addProperty('color_secondary', basestring, required=True, cast=validateHexColor)

# Set exceptions as list of exceptions 
exceptions = account_exceptions

@require_http_methods(["POST"])
@stamped_http_api_request(form=HTTPForm, exceptions=exceptions)
def run(request, auth_user_id, data, **kwargs):
    account = account_api.customizeStamp(auth_user_id, data)
    user = HTTPUser().importUser(account)
    result = user.dataExport()

    return json_response(result)

