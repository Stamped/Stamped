#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import logs

from errors import StampedMissingParametersError, StampedFacebookTokenError, StampedLinkedAccountError, StampedThirdPartyError
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
        cls.addProperty('service_name', basestring, required=True)
        cls.addProperty('stamp_id', basestring, required=True)
        cls.addProperty('temp_image_url', basestring)

# Set exceptions as list of exceptions 
exceptions = [
    (StampedMissingParametersError, 400, 'bad_request', 'Missing third party service name'),
    (StampedFacebookTokenError, 401, 'facebook_auth', "Facebook login failed. Please reauthorize your account."),
    (StampedLinkedAccountError, 401, 'invalid_credentials', "Missing credentials for linked account."),
    (StampedThirdPartyError, 400, 'third_party', "There was an error connecting to the third-party service."),
] + stamp_exceptions

@require_http_methods(["POST"])
@stamped_http_api_request(form=HTTPForm, exceptions=exceptions)
def run(request, auth_user_id, form, **kwargs):
    if form.service_name is None:
        if 'service_name' not in kwargs:
            raise StampedMissingParametersError("Missing linked account service name")
        form.service_name = kwargs['service_name']

    stamp = stamp_api.shareStamp(auth_user_id, stampId=form.stamp_id, serviceName=form.service_name, 
        imageUrl=form.temp_image_url)

    result = HTTPStamp().import_stamp(stamp).data_export()

    return json_response(result)

