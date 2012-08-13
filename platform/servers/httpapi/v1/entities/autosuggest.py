#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import logs

from schema import Schema
from api_old.Schemas import Coordinates
from api_old.SchemaValidation import validateCategory, validateCoordinates
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
        cls.addProperty('query', basestring, required=True) 
        cls.addProperty('category', basestring, required=True, cast=validateCategory)
        cls.addProperty('coordinates', basestring, cast=validateCoordinates)

    def exportCoordinates(self):
        if self.coordinates is not None:
            try:
                coordinates = self.coordinates.split(',')
                return Coordinates().data_import({'lat': coordinates[0], 'lng': coordinates[1]})
            except Exception as e:
                logs.warning("Unable to parse coordinates '%s': %s %s" % (self.coordinates, type(e), e))

        return None

# Set exceptions as list of exceptions 
exceptions = entity_exceptions

@require_http_methods(["GET"])
@stamped_http_api_request(requires_auth=False, form=HTTPForm, exceptions=exceptions)
def run(request, auth_user_id, form, **kwargs):

    result = entity_api.getEntityAutoSuggestions(query=form.query, category=form.category,
        coordinates=form.exportCoordinates(), authUserId=auth_user_id)

    return json_response(result)

