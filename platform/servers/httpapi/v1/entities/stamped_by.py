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
from servers.httpapi.v1.schemas import HTTPStampedBy
from servers.httpapi.v1.entities.errors import entity_exceptions

# APIs
entity_api = EntityAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id', basestring, required=True)

# Set exceptions as list of exceptions 
exceptions = entity_exceptions

@require_http_methods(["GET"])
@stamped_http_api_request(requires_auth=False, form=HTTPForm, exceptions=exceptions)
def run(request, auth_user_id, form, **kwargs):
    stamped_by = entity_api.entityStampedBy(form.entity_id, auth_user_id)

    result = HTTPStampedBy().importStampedBy(stamped_by).dataExport()

    return json_response(result)

