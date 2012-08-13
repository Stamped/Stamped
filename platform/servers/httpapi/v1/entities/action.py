#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import logs

from schema import Schema
from api.entityapi import EntityAPI
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
from servers.httpapi.v1.entities.errors import entity_exceptions

# APIs
entity_api = EntityAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('action', basestring)
        cls.addProperty('source', basestring)
        cls.addProperty('source_id', basestring)
        cls.addProperty('entity_id', basestring)
        cls.addProperty('user_id', basestring)
        cls.addProperty('stamp_id', basestring)

# Set exceptions as list of exceptions 
exceptions = entity_exceptions

@require_http_methods(["POST"])
@stamped_http_api_request(form=HTTPForm, exceptions=exceptions)
def run(request, auth_user_id, form, **kwargs):
    # Hack for Python 2.6 where unicode keys aren't valid...
    data = {}
    for k, v in form.dataExport().items():
        data[str(k)] = v
    
    result = entity_api.completeAction(auth_user_id, **data)

    ### TODO: Convert result into standardized output

    return json_response(result)

