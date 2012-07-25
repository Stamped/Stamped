#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from servers.httpapi.v0.helpers import *

try:
    from resolve        import ManualEdit
except:
    raise

entityExceptions = [
    (StampedEntityUpdatePermissionError,   403, 'invalid_credentials', "Insufficient privileges to update entity"),
    (StampedTombstonedEntityError,         400, 'invalid_credentials', "Sorry, this entity can no longer be updated"),
    (StampedInvalidCategoryError,          400, 'bad_request',         "Invalid category"),
    (StampedInvalidSubcategoryError,       400, 'bad_request',         "Invalid subcategory"),
    (StampedMenuUnavailableError,          404, 'not_found',           "Menu is unavailable"),
]

def _convertHTTPEntity(entity,
                       authClientId=None):
    client = stampedAuth.getClientDetails(authClientId)
    
    if authClientId is not None and client.api_version < 1:
        raise NotImplementedError
    else:
        return HTTPEntity().importEntity(entity, client)


@require_http_methods(["POST"])
@handleHTTPRequest(http_schema=HTTPEntityNew,
                   exceptions=entityExceptions)
def create(request, authUserId, authClientId, http_schema, **kwargs):
    entity          = http_schema.exportEntity(authUserId)
    
    entity          = stampedAPI.addEntity(entity)
    entity          = _convertHTTPEntity(entity, authClientId)
    
    return transformOutput(entity.dataExport())


@require_http_methods(["GET"])
@handleHTTPRequest(requires_auth=False,
                   http_schema=HTTPEntityIdSearchId,
                   exceptions=entityExceptions)
def show(request, authUserId, authClientId, http_schema, uri, **kwargs):
    try:
        return getCache(uri, http_schema)
    except KeyError:
        pass
    except Exception as e:
        logs.warning("Failed to get cache: %s" % e)
            
    entity      = stampedAPI.getEntity(http_schema, authUserId)
    entity      = _convertHTTPEntity(entity, authClientId)

    result = transformOutput(entity.dataExport())

    # setCache(uri, http_schema, result, ttl=1800)
    
    return result


@require_http_methods(["POST"])
@handleHTTPRequest(http_schema=HTTPEntityId,
                   exceptions=entityExceptions)
def remove(request, authUserId, authClientId, http_schema, **kwargs):
    entity = stampedAPI.removeCustomEntity(authUserId, http_schema.entity_id)
    entity = _convertHTTPEntity(entity, authClientId)

    return transformOutput(entity.dataExport())


@require_http_methods(["GET"])
@handleHTTPRequest(requires_auth=False,
                   http_schema=HTTPEntitySearchRequest,
                   exceptions=entityExceptions)
def autosuggest(request, authUserId, http_schema, **kwargs):
    result = stampedAPI.getEntityAutoSuggestions(query=http_schema.query, 
                                                 category=http_schema.category,
                                                 coordinates=http_schema.exportCoordinates(),
                                                 authUserId=authUserId)

    return transformOutput(result)


@require_http_methods(["GET"])
@handleHTTPRequest(http_schema=HTTPEntitySearchRequest,
                   exceptions=entityExceptions)
def search(request, authUserId, http_schema, **kwargs):
    result = stampedAPI.searchEntities(authUserId=authUserId, 
                                       query=http_schema.query, 
                                       category=http_schema.category,
                                       coords=http_schema.exportCoordinates())
    
    group = HTTPEntitySearchResultsGroup()
    group.title = 'Search results'
    if http_schema.category == 'place':
        group.image_url = 'http://static.stamped.com/assets/icons/default/search_google.png'

    entities = []
    for entity, distance in result:
        try:
            entities.append(HTTPEntitySearchResultsItem().importEntity(entity, distance))
        except Exception as e:
            logs.warning('HTTPEntitySearchResultsItem Import Error: %s (entity = %s)' % (e, entity))

    group.entities = entities 
    
    return transformOutput(group.dataExport())


@require_http_methods(["GET"])
@handleHTTPRequest(http_schema=HTTPEntitySuggestionRequest,
                   exceptions=entityExceptions)
def suggested(request, authUserId, http_schema, **kwargs):
    sections    = stampedAPI.getSuggestedEntities(authUserId=authUserId, 
                                                  category=http_schema.category,
                                                  subcategory=http_schema.subcategory,
                                                  coordinates=http_schema.exportCoordinates(),
                                                  limit=20)

    convert     = lambda e: HTTPEntitySearchResultsItem().importEntity(e)
    result      = []

    for section in sections:
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
    
    return transformOutput(result)


@require_http_methods(["GET"])
@handleHTTPRequest(requires_auth=False,
                   http_schema=HTTPEntityId,
                   exceptions=entityExceptions)
def menu(request, authUserId, http_schema, **kwargs):
    menu        = stampedAPI.getMenu(http_schema.entity_id)
    http_menu   = HTTPMenu().importMenu(menu)
    
    return transformOutput(http_menu.dataExport())


@handleHTTPRequest(requires_auth=False,
                   http_schema=HTTPEntityId,
                   exceptions=entityExceptions)
@require_http_methods(["GET"])
def stampedBy(request, authUserId, http_schema, **kwargs):
    result = stampedAPI.entityStampedBy(http_schema.entity_id, authUserId)
    result = HTTPStampedBy().importStampedBy(result)
    return transformOutput(result.dataExport())


@require_http_methods(["POST"])
@handleHTTPRequest(http_schema=HTTPActionComplete,
                   exceptions=entityExceptions)
def completeAction(request, authUserId, http_schema, **kwargs):
    # Hack for Python 2.6 where unicode keys aren't valid...
    data = {}
    for k, v in http_schema.dataExport().items():
        data[str(k)] = v
    
    result = stampedAPI.completeAction(authUserId, **data)
    return transformOutput(result)

_secret = 'supersmash'

@require_http_methods(["GET"])
@handleHTTPRequest(http_schema=HTTPEntityEdit, requires_auth=False)
def edit(request, authUserId, http_schema, **kwargs):
    if _secret != http_schema.secret:
        raise StampedHTTPError(403, 'Not authorized')
    form = ManualEdit.formForEntity(http_schema.entity_id, secret=http_schema.secret)
    kwargs = {}
    kwargs.setdefault('content_type', 'text/javascript; charset=UTF-8')
    kwargs.setdefault('mimetype', 'text/html')
    output      = HttpResponse(form, **kwargs)
    
    return output


@require_http_methods(["POST"])
@handleHTTPRequest(http_schema=HTTPEntityUpdate, requires_auth=False)
def update(request, authUserId, http_schema, **kwargs):
    if _secret != http_schema.secret:
        raise StampedHTTPError(403, 'Not authorized')
    # try:
    ManualEdit.update(http_schema)
    # except Exception as e:
    #     raise StampedHTTPError(400, 'bad form: %s' % e)

    form = ManualEdit.formForEntity(http_schema.entity_id, secret=http_schema.secret)
    kwargs = {}
    kwargs.setdefault('content_type', 'text/javascript; charset=UTF-8')
    kwargs.setdefault('mimetype', 'text/html')
    output      = HttpResponse(form, **kwargs)
    
    return output
