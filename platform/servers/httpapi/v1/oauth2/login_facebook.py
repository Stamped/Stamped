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
        # Paging
        cls.addProperty('before', int)
        cls.addProperty('limit', int)
        cls.addProperty('offset', int)

        # Scope
        cls.addProperty('stamp_id', basestring, cast=validateStampId)

    @property
    def before_timestamp(self):
        if self.before is not None:
            return datetime.utcfromtimestamp(int(self.before))
        return None

# Set exceptions as list of exceptions 
exceptions = comment_exceptions

@require_http_methods(["GET"])
@stamped_http_api_request(form=HTTPForm, exceptions=exceptions)
def run(request, auth_user_id, form, **kwargs):
    comments = comment_api.getComments(form.stamp_id, auth_user_id, before=form.before_timestamp, 
        limit=form.limit, offset=form.offset)

    result = []
    for comment in comments:
        result.append(HTTPComment().importComment(comment).data_export())

    return json_response(result)

