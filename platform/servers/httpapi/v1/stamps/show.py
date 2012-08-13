#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import logs

from errors import StampedInputError
from schema import Schema
from api.stampapi import StampAPI
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
from servers.httpapi.v1.schemas import HTTPStamp
from servers.httpapi.v1.stamps.errors import stamp_exceptions

# APIs
stamp_api = StampAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id', basestring)
        cls.addProperty('user_id', basestring)
        cls.addProperty('stamp_num', int)

# Set exceptions as list of exceptions 
exceptions = stamp_exceptions

@require_http_methods(["GET"])
@stamped_http_api_request(requires_auth=False, form=HTTPForm, exceptions=exceptions)
def run(request, auth_user_id, form, **kwargs):

    ### RESTRUCTURE TODO: Add caching

    if form.stamp_id is not None:
        stamp = stamp_api.getStamp(form.stamp_id, auth_user_id)
    elif form.user_id is not None and form.stamp_num is not None:
        stamp = stamp_api.getStampFromUser(userId=form.user_id, stampNumber=form.stamp_num)
    else:
        raise StampedInputError("Invalid request")

    result = HTTPStamp().import_stamp(stamp).data_export()

    return json_response(result)

