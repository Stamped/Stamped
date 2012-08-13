#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from api.stampapi import StampAPI
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
from servers.httpapi.v1.schemas import HTTPSearchSlice, HTTPStamp
from servers.httpapi.v1.stamps.errors import stamp_exceptions

# APIs
stamp_api = StampAPI()

# Set exceptions as list of exceptions 
exceptions = stamp_exceptions

@require_http_methods(["GET"])
@stamped_http_api_request(requires_auth=False, form=HTTPSearchSlice, conversion=HTTPSearchSlice.exportTimeSlice, 
    exceptions=exceptions)
def run(request, auth_user_id, schema, **kwargs):

    ### RESTRUCTURE TODO: Add caching

    stamps = stamp_api.searchStampCollection(schema, auth_user_id)

    result = []
    for stamp in stamps:
        try:
            result.append(HTTPStamp().import_stamp(stamp).data_export())
        except Exception as e:
            logs.warning("Unable to convert stamp '%s': %s %s" % (stamp, type(e), e))

    return json_response(result)

