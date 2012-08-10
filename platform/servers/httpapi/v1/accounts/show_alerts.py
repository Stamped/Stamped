#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from api.accountapi import AccountAPI
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
from servers.httpapi.v1.accounts.errors import account_exceptions
from servers.httpapi.v1.accounts.helpers import build_alert_response

# APIs
account_api = AccountAPI()

# Set exceptions as list of exceptions 
exceptions = account_exceptions

@require_http_methods(["GET"])
@stamped_http_api_request(exceptions=exceptions)
def run(request, auth_user_id, **kwargs):
    account = account_api.get(auth_user_id)
    result = build_alert_response(account)

    return json_response(result)

