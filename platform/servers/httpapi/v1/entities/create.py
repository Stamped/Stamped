#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import logs
import datetime

from schema import Schema
from api_old.Schemas import PersonEntityMini, MediaCollectionEntityMini, BasicEntityMini, Coordinates
from api_old.SchemaValidation import validateString, validateCategory, validateSubcategory, validateCoordinates
from api_old import Entity
from api.entityapi import EntityAPI
from django.views.decorators.http import require_http_methods
from servers.httpapi.v1.helpers import stamped_http_api_request, json_response
from servers.httpapi.v1.schemas import HTTPEntity
from servers.httpapi.v1.entities.errors import entity_exceptions

# APIs
entity_api = EntityAPI()

# Define input form as schema object
class HTTPForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('title',                            basestring, required=True, cast=validateString)
        cls.addProperty('category',                         basestring, required=True, cast=validateCategory)
        cls.addProperty('subcategory',                      basestring, required=True, cast=validateSubcategory)
        cls.addProperty('subtitle',                         basestring, cast=validateString)
        cls.addProperty('desc',                             basestring, cast=validateString)

        cls.addProperty('address_street',                   basestring)
        cls.addProperty('address_street_ext',               basestring)
        cls.addProperty('address_locality',                 basestring)
        cls.addProperty('address_region',                   basestring)
        cls.addProperty('address_postcode',                 basestring)
        cls.addProperty('address_country',                  basestring) ### TODO: Add cast to check ISO code

        cls.addProperty('coordinates',                      basestring, cast=validateCoordinates)
        cls.addProperty('year',                             int) 
        cls.addProperty('artist',                           basestring)
        cls.addProperty('album',                            basestring)
        cls.addProperty('author',                           basestring)
        cls.addProperty('network',                          basestring)
        cls.addProperty('director',                         basestring)
        cls.addProperty('genre',                            basestring)

    def export_entity(self, auth_user_id):
        """
        Convert the HTTPForm for a new entity into an entity schema object.
        """

        ### RESTRUCTURE TODO: Better centralization of Entity helper functions
        ### RESTRUCTURE TODO: Clean up in general

        kind    = list(Entity.mapSubcategoryToKinds(self.subcategory))[0]
        entity  = Entity.buildEntity(kind=kind)

        entity.schema_version   = 0
        entity.types            = list(Entity.mapSubcategoryToTypes(self.subcategory))
        entity.title            = self.title

        def addField(entity, field, value, timestamp):
            if value is not None and value != '':
                try:
                    setattr(entity, field, value)
                    setattr(entity, '%s_source' % field, 'seed')
                    setattr(entity, '%s_timestamp' % field, timestamp)
                except AttributeError:
                    pass

        def addListField(entity, field, value, entityMini=None, timestamp=None):
            if value is not None and value != '':
                try:
                    if entityMini is not None:
                        item = entityMini()
                        item.title = value
                    else:
                        item = value
                    getattr(entity, field).append(item)
                    setattr(entity, '%s_source' % field, 'seed')
                    setattr(entity, '%s_timestamp' % field, timestamp)
                except AttributeError:
                    pass

        now = datetime.datetime.utcnow()

        addField(entity, 'desc', self.desc, now)

        if self.year is not None:
            try:
                addField(entity, 'release_date', datetime.datetime(int(self.year), 1, 1), timestamp=now)
            except ValueError as e:
                logs.warning("Invalid year '%s': %s %s" % (self.year, type(e), e))

        addField(entity, 'address_street', self.address_street, timestamp=now)
        addField(entity, 'address_street_ext', self.address_street_ext, timestamp=now)
        addField(entity, 'address_locality', self.address_locality, timestamp=now)
        addField(entity, 'address_region', self.address_region, timestamp=now)
        addField(entity, 'address_postcode', self.address_postcode, timestamp=now)
        # Only add country if other fields are set, too
        if self.address_street is not None or self.address_locality is not None \
            or self.address_region is not None or self.address_postcode is not None:
            addField(entity, 'address_country', self.address_country, timestamp=now)

        addListField(entity, 'artists', self.artist, PersonEntityMini, timestamp=now)
        addListField(entity, 'collections', self.album, MediaCollectionEntityMini, timestamp=now)
        addListField(entity, 'authors', self.author, PersonEntityMini, timestamp=now)
        addListField(entity, 'networks', self.network, BasicEntityMini, timestamp=now)
        addListField(entity, 'directors', self.director, PersonEntityMini, timestamp=now)
        addListField(entity, 'genres', self.genre, timestamp=now)

        if self.coordinates is not None:
            try:
                coordinates = self.coordinates.split(',')
                coordinates = Coordinates().data_import({'lat': coordinates[0], 'lng': coordinates[1]})
                addField(entity, 'coordinates', coordinates, now)
            except Exception as e:
                logs.warning("Unable to parse coordinates '%s': %s %s" % (self.coordinates, type(e), e))

        entity.sources.user_generated_id = auth_user_id
        entity.sources.user_generated_timestamp = now
        if self.subtitle is not None and self.subtitle != '':
            entity.sources.user_generated_subtitle = self.subtitle

        return entity


# Set exceptions as list of exceptions 
exceptions = entity_exceptions

@require_http_methods(["POST"])
@stamped_http_api_request(form=HTTPForm, exceptions=exceptions)
def run(request, auth_user_id, form, **kwargs):
    entity = form.export_entity(auth_user_id)
    entity = entity_api.addEntity(entity)

    result = HTTPEntity().importEntity(entity).dataExport()

    return json_response(result)

