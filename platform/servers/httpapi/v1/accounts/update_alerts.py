#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from schema import Schema
from api.accountapi import AccountAPI
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
from servers.httpapi.v1.accounts.errors import account_exceptions
from servers.httpapi.v1.accounts.helpers import build_alert_response

# APIs
account_api = AccountAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('on', basestring)
        cls.addProperty('off', basestring)

# Set exceptions as list of exceptions 
exceptions = account_exceptions

@require_http_methods(["POST"])
@stamped_http_api_request(form=HTTPForm, exceptions=exceptions)
def run(request, auth_user_id, form, **kwargs):
    on = None
    if form.on is not None:
        on = set(form.on.split(','))

    off = None
    if form.off is not None:
        off = set(form.off.split(','))

    account = account_api.updateAlerts(auth_user_id, on, off)
    result = build_alert_response(account)

    return json_response(result)

