#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import logs

from schema import Schema
from api.stampapi import StampAPI
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
from servers.httpapi.v1.schemas import HTTPEntity
from servers.httpapi.v1.stamps.errors import stamp_exceptions

# APIs
stamp_api = StampAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id', basestring, required=True)

# Set exceptions as list of exceptions 
exceptions = stamp_exceptions

@require_http_methods(["POST"])
@stamped_http_api_request(form=HTTPForm, exceptions=exceptions)
def run(request, auth_user_id, form, **kwargs):
    stamp_api.removeStamp(auth_user_id, form.stamp_id)

    return json_response(True)

