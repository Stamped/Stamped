#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from schema import Schema
from api_old.SchemaValidation import validateEmails
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
        cls.addProperty('emails', basestring, cast=validateEmails)

# Set exceptions as list of exceptions 
exceptions = friendship_exceptions

@require_http_methods(["POST"])
@stamped_http_api_request(form=HTTPForm, exceptions=exceptions)
def run(request, auth_user_id, form, **kwargs):
    ### TODO: This should not be passing the form!
    emails = form.emails.split(',')
    friendship_api.inviteFriends(auth_user_id, emails)

    return json_response(True)

