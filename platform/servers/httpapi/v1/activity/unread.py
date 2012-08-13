#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import logs

from schema import Schema
from api.activityapi import ActivityAPI
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
from servers.httpapi.v1.schemas import HTTPActivity
from servers.httpapi.v1.activity.errors import activity_exceptions

# APIs
activity_api = ActivityAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        # Paging
        cls.addProperty('limit', int)
        cls.addProperty('offset', int)

        # Scope
        cls.addProperty('scope', basestring) # me, friends

    def __init__(self):
        Schema.__init__(self)
        self.limit = 20
        self.offset = 0

# Set exceptions as list of exceptions 
exceptions = activity_exceptions

@require_http_methods(["GET"])
@stamped_http_api_request(form=HTTPForm, exceptions=exceptions)
def run(request, auth_user_id, form, **kwargs):
    count = activity_api.getUnreadActivityCount(auth_user_id)
    
    result = {'num_unread': count}

    return json_response(result)

