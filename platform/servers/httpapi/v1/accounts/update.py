#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from api_old.Schemas import AccountUpdateForm

from schema import Schema
from errors import StampedInternalError
from api.accountapi import AccountAPI
from api_old.SchemaValidation import validateURL, validateHexColor, validateScreenName, parsePhoneNumber
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
from servers.httpapi.v1.accounts.errors import account_exceptions
from servers.httpapi.v1.schemas import HTTPUser, convertPhoneToInt

# APIs
account_api = AccountAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name',                             basestring)
        cls.addProperty('screen_name',                      basestring, cast=validateScreenName)
        cls.addProperty('phone',                            basestring, cast=parsePhoneNumber)

        cls.addProperty('bio',                              basestring)
        cls.addProperty('website',                          basestring, cast=validateURL)
        cls.addProperty('location',                         basestring)
        cls.addProperty('color_primary',                    basestring, cast=validateHexColor)
        cls.addProperty('color_secondary',                  basestring, cast=validateHexColor)

        cls.addProperty('temp_image_url',                   basestring, cast=validateURL)

    def convertToAccountUpdateForm(self):
        data = self.dataExport()
        if 'phone' in data:
            data['phone'] = convertPhoneToInt(data['phone'])

        return AccountUpdateForm().dataImport(data, overflow=True)

# Set exceptions as list of exceptions 
exceptions = [
    (StampedInternalError, 400, 'internal', 'There was a problem updating the account. Please try again later.'),
] + account_exceptions

@require_http_methods(["POST"])
@stamped_http_api_request(form=HTTPForm, conversion=HTTPForm.convertToAccountUpdateForm, exceptions=exceptions)
def run(request, auth_user_id, schema, **kwargs):
    account = account_api.updateAccount(auth_user_id, schema)
    user = HTTPUser().importUser(account)
    result = user.dataExport()

    return json_response(result)

