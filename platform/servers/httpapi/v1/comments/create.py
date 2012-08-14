#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from schema import Schema
from api_old.SchemaValidation import validateStampId
from api.commentapi import CommentAPI
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
from servers.httpapi.v1.schemas import HTTPComment
from servers.httpapi.v1.comments.errors import comment_exceptions

# APIs
comment_api = CommentAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id', basestring, required=True, cast=validateStampId)
        cls.addProperty('blurb', basestring, required=True)

# Set exceptions as list of exceptions 
exceptions = comment_exceptions

@require_http_methods(["POST"])
@stamped_http_api_request(form=HTTPForm, exceptions=exceptions)
def run(request, auth_user_id, form, **kwargs):
    comment = comment_api.addComment(auth_user_id, form.stamp_id, form.blurb)

    result = HTTPComment().importComment(comment).data_export()
    
    return json_response(result)

