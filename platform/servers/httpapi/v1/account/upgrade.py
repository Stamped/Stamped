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
from api_old.SchemaValidation import validateString
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
        cls.addProperty('email', basestring, required=True)
        cls.addProperty('password', basestring, required=True, cast=validateString)

# Set exceptions as list of exceptions 
exceptions = [
    (StampedInternalError, 400, 'internal', 'There was a problem upgrading the account. Please try again later.'),
] + account_exceptions


@require_http_methods(["POST"])
@stamped_http_api_request(requires_client=True,
                            form=HTTPForm, 
                            parse_request_kwargs={'obfuscate':['password']},
                            exceptions=exceptions)
def run(request, client_id, auth_user_id, form, **kwargs):
    account = account_api.upgradeAccount(auth_user_id, form.email, form.password)
    user = HTTPUser().importAccount(account)

    token = oauth_api.addRefreshToken(client_id, user.user_id)
    result = {'user': user.dataExport(), 'token': token}

    return json_response(result)

