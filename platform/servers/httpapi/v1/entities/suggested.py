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
from servers.httpapi.v1.schemas import HTTPEntitySearchResultsGroup, HTTPEntitySearchResultsItem
from servers.httpapi.v1.entities.errors import entity_exceptions

# APIs
entity_api = EntityAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('category', basestring, required=True, cast=validateCategory)
        cls.addProperty('subcategory', basestring)
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
@stamped_http_api_request(form=HTTPForm, exceptions=exceptions)
def run(request, auth_user_id, form, **kwargs):

    suggestions = entity_api.getSuggestedEntities(authUserId=auth_user_id, category=form.category,
        subcategory=form.subcategory, coordinates=form.exportCoordinates(), limit=20)

    convert = lambda x: HTTPEntitySearchResultsItem().importEntity(x)
    result = []

    for section in suggestions:
        try:
            group = HTTPEntitySearchResultsGroup()
            group.title = 'Suggested'
            if http_schema.category == 'place':
                group.image_url = 'http://static.stamped.com/assets/icons/default/search_google.png'
            if 'name' in section and section['name'] is not None:
                group.title = section['name']
            group.entities = map(convert, section['entities'])

            result.append(group.dataExport())
        except Exception as e:
            logs.warning("Autosuggest error: %s (%s)" % (e, section))

    return json_response(result)

