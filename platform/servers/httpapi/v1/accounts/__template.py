#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from schema import Schema
# from api_old.SchemaValidation import *
# from api.likeapi import LikeAPI
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
# from servers.httpapi.v1.likes.errors import like_exceptions
# from servers.httpapi.v1.schemas import HTTPStamp

# like_api = LikeAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        # cls.addProperty('stamp_id', basestring, cast=validate_stamp_id)

# Define exceptions as list of exceptions 
exceptions = like_exceptions

@require_http_methods(["POST"])
@stamped_http_api_request(form=HTTPForm, exceptions=exceptions)
def run(request, auth_user_id, data, **kwargs):
	
	result = None

    return json_response(result)


