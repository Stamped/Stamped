#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *

def _convertHTTPEntity(entity, authClientId=None):
    client = stampedAuth.getClientDetails(authClientId)
    
    if authClientId is not None and client.api_version < 1:
        raise NotImplementedError
    else:
        return HTTPEntity().importEntity(entity, client)


@handleHTTPRequest(http_schema=HTTPEntityNew)
@require_http_methods(["POST"])
def create(request, authUserId, authClientId, http_schema, **kwargs):
    entity          = http_schema.exportEntity(authUserId)
    
    entity          = stampedAPI.addEntity(entity)
    entity          = _convertHTTPEntity(entity, authClientId)
    
    return transformOutput(entity.dataExport())


@handleHTTPRequest(requires_auth=False, http_schema=HTTPEntityIdSearchId)
@require_http_methods(["GET"])
def show(request, authUserId, authClientId, http_schema, **kwargs):
    entity      = stampedAPI.getEntity(http_schema, authUserId)
    entity      = _convertHTTPEntity(entity, authClientId)
    
    return transformOutput(entity.dataExport())


@handleHTTPRequest(http_schema=HTTPEntityId)
@require_http_methods(["POST"])
def remove(request, authUserId, authClientId, http_schema, **kwargs):
    entity = stampedAPI.removeCustomEntity(authUserId, http_schema.entity_id)
    entity = _convertHTTPEntity(entity, authClientId)

    return transformOutput(entity.dataExport())


@handleHTTPRequest(http_schema=HTTPEntitySearchRequest)
@require_http_methods(["GET"])
def autosuggest(request, authUserId, http_schema, **kwargs):
    result = stampedAPI.getEntityAutoSuggestions(authUserId=authUserId, 
                                                 query=http_schema.query, 
                                                 category=http_schema.category,
                                                 coordinates=http_schema.exportCoordinates())

    return transformOutput(result)


@handleHTTPRequest(http_schema=HTTPEntitySearchRequest)
@require_http_methods(["GET"])
def search(request, authUserId, http_schema, **kwargs):
    result = stampedAPI.searchEntities(authUserId=authUserId, 
                                       query=http_schema.query, 
                                       category=http_schema.category,
                                       coords=http_schema.exportCoordinates())
    
    group = HTTPEntitySearchResultsGroup()
    group.title = 'Search results'

    entities = []
    for entity, distance in result:
        try:
            entities.append(HTTPEntitySearchResultsItem().importEntity(entity, distance))
        except Exception as e:
            logs.warning('HTTPEntitySearchResultsItem Import Error: %s (entity = %s)' % (e, entity))

    group.entities = entities 
    
    return transformOutput(group.dataExport())


@handleHTTPRequest(http_schema=HTTPEntitySuggestionRequest)
@require_http_methods(["GET"])
def suggested(request, authUserId, http_schema, **kwargs):
    sections    = stampedAPI.getSuggestedEntities(authUserId=authUserId, 
                                                  category=http_schema.category,
                                                  subcategory=http_schema.subcategory,
                                                  coordinates=http_schema.exportCoordinates(),
                                                  limit=http_schema.limit)

    convert     = lambda e: HTTPEntitySearchResultsItem().importEntity(e)
    result      = []

    for section in sections:
        try:
            group = HTTPEntitySearchResultsGroup()
            group.title = 'Suggested'
            if 'name' in section and section['name'] is not None:
                group.title = section['name']
            group.entities = map(convert, section['entities'])

            result.append(group.dataExport())
        except Exception as e:
            logs.warning("Autosuggest error: %s (%s)" % (e, section))
    
    return transformOutput(result)


@handleHTTPRequest(requires_auth=False, http_schema=HTTPEntityId)
@require_http_methods(["GET"])
def menu(request, authUserId, http_schema, **kwargs):
    menu        = stampedAPI.getMenu(http_schema.entity_id)
    http_menu   = HTTPMenu().importMenu(menu)
    
    return transformOutput(http_menu.dataExport())


@handleHTTPRequest(requires_auth=False, http_schema=HTTPEntityId)
@require_http_methods(["GET"])
def stampedBy(request, authUserId, http_schema, **kwargs):
    result = stampedAPI.entityStampedBy(http_schema.entity_id, authUserId)
    result = HTTPStampedBy().importStampedBy(result)
    return transformOutput(result.dataExport())


@handleHTTPRequest(requires_auth=False, http_schema=HTTPActionComplete)
@require_http_methods(["POST"])
def completeAction(request, http_schema, **kwargs):
    authUserId, authClientId = checkOAuth(request)
    
    #schema      = parseRequest(HTTPActionComplete(), request)
    logs.info('http_schema: %s' % http_schema)
    data = {}
    # Hack for Python 2.6 where unicode keys aren't valid...
    for k, v in http_schema.dataExport().items():
        data[str(k)] = v
    result      = stampedAPI.completeAction(authUserId, **data)

    return transformOutput(result)

