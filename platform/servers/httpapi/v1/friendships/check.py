#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from schema import Schema
from api_old.SchemaValidation import validateUserId, validateScreenName
from api.friendshipapi import FriendshipAPI
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
from servers.httpapi.v1.friendships.errors import friendship_exceptions

# APIs
friendship_api = FriendshipAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id_a', basestring, cast=validateUserId)
        cls.addProperty('screen_name_a', basestring, cast=validateScreenName)
        cls.addProperty('user_id_b', basestring, cast=validateUserId)
        cls.addProperty('screen_name_b', basestring, cast=validateScreenName)

# Set exceptions as list of exceptions 
exceptions = friendship_exceptions

@require_http_methods(["GET"])
@stamped_http_api_request(form=HTTPForm, exceptions=exceptions)
def run(request, auth_user_id, form, **kwargs):
    ### TODO: This should not be passing the form!
    result = friendship_api.checkFriendship(auth_user_id, form)

    return json_response(result)

