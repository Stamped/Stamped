#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from errors import StampedInputError
from schema import Schema
from api.guideapi import GuideAPI
from api_old.Schemas import GuideRequest
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
from servers.httpapi.v1.schemas import convertViewport, HTTPEntity
from servers.httpapi.v1.guide.errors import guide_exceptions

# APIs
guide_api = GuideAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        def validateSection(section):
            if section is None:
                return None
            section = section.lower()
            if section in set(['food', 'music', 'film', 'book', 'app']):
                return section 
            raise StampedInputError("Invalid section: %s" % section)

        def validateSubsection(subsection):
            if subsection is None:
                return None
            subsection = subsection.lower()
            if subsection in set(['restaurant', 'bar', 'cafe', 'artist', 'album', 'track', 'movie', 'tv']):
                return subsection
            raise StampedInputError("Invalid subsection: %s" % subsection)

        def validateScope(scope):
            if scope is None:
                return None
            scope = scope.lower()
            ### TEMP
            if scope == 'everyone':
                scope = 'popular'
            if scope in set(['me', 'inbox', 'popular']):
                return scope 
            raise StampedInputError("Invalid scope: %s" % scope)


        cls.addProperty('limit',                            int)
        cls.addProperty('offset',                           int)
        cls.addProperty('section',                          basestring, required=True, cast=validateSection)
        cls.addProperty('subsection',                       basestring, cast=validateSubsection)
        cls.addProperty('viewport',                         basestring, cast=validateViewport)
        cls.addProperty('scope',                            basestring, required=True, cast=validateScope)

    def exportGuideRequest(self):
        data = self.dataExport()
        if 'viewport' in data:
            del(data['viewport'])
        guideRequest = GuideRequest()
        guideRequest.dataImport(data)

        if self.viewport is not None:
            guideRequest.viewport = convertViewport(self.viewport)

        return guideRequest

# Set exceptions as list of exceptions 
exceptions = guide_exceptions

@require_http_methods(["GET"])
@stamped_http_api_request(requires_auth=False, form=HTTPForm, conversion=HTTPForm.export_guide_request, 
    exceptions=exceptions)
def run(request, auth_user_id, schema, **kwargs):

    ### RESTRUCTURE TODO: Add caching

    try:
        entities = guide_api.searchGuide(schema, auth_user_id)
    except Exception as e:
        logs.warning("Failed to get guide: %s %s" % (type(e), e))
        entities = []

    result = []
    for entity in entities:
        try:
            result.append(HTTPEntity().importEntity(entity).data_export())
        except Exception as e:
            logs.warning("Unable to convert entity '%s': %s %s" % (entity, type(e), e))

    return json_response(result)

