#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import logs

from schema import Schema
from api.accountapi import AccountAPI
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
from servers.httpapi.v1.accounts.errors import account_exceptions
from servers.httpapi.v1.schemas import HTTPAccount

# APIs
account_api = AccountAPI()

# Set exceptions as list of exceptions 
exceptions = account_exceptions

@require_http_methods(["POST"])
@stamped_http_api_request(exceptions=exceptions)
def run(request, auth_user_id, **kwargs):
    account = account_api.removeAccount(auth_user_id)
    account = HTTPAccount().importAccount(account)
    result = account.dataExport()

    return json_response(result)

