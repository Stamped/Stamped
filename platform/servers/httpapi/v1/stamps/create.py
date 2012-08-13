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
from servers.httpapi.v1.schemas import HTTPStamp
from servers.httpapi.v1.stamps.errors import stamp_exceptions

# APIs
stamp_api = StampAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id', basestring)
        cls.addProperty('search_id', basestring)
        cls.addProperty('blurb', basestring)
        cls.addProperty('credits', basestring) # comma-separated screen names
        cls.addProperty('temp_image_url', basestring)

# Set exceptions as list of exceptions
exceptions = stamp_exceptions

@require_http_methods(["POST"])
@stamped_http_api_request(form=HTTPForm, exceptions=exceptions)
def run(request, auth_user_id, data, **kwargs):
    entity_request = {
        'entity_id' : data.pop('entity_id', None),
        'search_id' : data.pop('search_id', None),
    }
    
    if 'credits' in data and data['credits'] is not None:
        data['credits'] = data['credits'].split(',')
    
    stamp = stamp_api.addStamp(auth_user_id, entity_request, data)
    
    result = HTTPStamp().import_stamp(stamp).dataExport()
    
    return json_response(result)

