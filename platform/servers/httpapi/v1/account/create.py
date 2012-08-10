#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import logs

from api_old.Schemas import Account

from schema import Schema
from api_old.SchemaValidation import validateEmail, validateString, validateURL, validateHexColor, validateScreenName, parsePhoneNumber
from api.accountapi import AccountAPI
from api.oauthapi import OAuthAPI
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
from servers.httpapi.v1.account.errors import account_exceptions
from servers.httpapi.v1.schemas import HTTPUser, convertPhoneToInt

# APIs
account_api = AccountAPI()
oauth_api = OAuthAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name',                             basestring, required=True)
        cls.addProperty('email',                            basestring, required=True, cast=validateEmail)
        cls.addProperty('password',                         basestring, required=True, cast=validateString)
        cls.addProperty('screen_name',                      basestring, required=True, cast=validateScreenName)
        cls.addProperty('phone',                            basestring, cast=parsePhoneNumber)

        cls.addProperty('bio',                              basestring)
        cls.addProperty('website',                          basestring, cast=validateURL)
        cls.addProperty('location',                         basestring)
        cls.addProperty('color_primary',                    basestring, cast=validateHexColor)
        cls.addProperty('color_secondary',                  basestring, cast=validateHexColor)

        # for asynchronous image uploads
        cls.addProperty('temp_image_url',                   basestring)

    def convertToAccount(self):
        data = self.dataExport()
        phone = convertPhoneToInt(data.pop('phone', None))
        if phone is not None:
            data['phone'] = phone

        return Account().dataImport(data, overflow=True)

# Set exceptions as list of exceptions 
exceptions = account_exceptions

@require_http_methods(["POST"])
@stamped_http_api_request(requires_auth=False,
                            requires_client=True,
                            form=HTTPForm, 
                            conversion=HTTPForm.convertToAccount,
                            parse_request_kwargs={'obfuscate':['password']},
                            exceptions=exceptions)
def run(request, client_id, form, schema, **kwargs):
    account = account_api.addAccount(schema, tempImageUrl=form.temp_image_url)
    user = HTTPUser().importAccount(account)
    logs.user(user.user_id)

    token = oauth_api.addRefreshToken(client_id, user.user_id)
    result = {'user': user.dataExport(), 'token': token}

    return json_response(result)

