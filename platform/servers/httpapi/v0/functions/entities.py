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

# @handleHTTPRequest(http_schema=HTTPEntityEdit)
# @require_http_methods(["POST"])
# def update(request, authUserId, authClientId, http_schema, data, **kwargs):
#     ### TEMP: Generate list of changes. Need to do something better eventually...
#     del(data['entity_id'])
    
#     for k, v in data.iteritems():
#         if v == '':
#             data[k] = None
#     if 'address' in data:
#         data['details.place.address'] = data['address']
#         del(data['address'])
#     if 'coordinates' in data and data['coordinates'] != None:
#         data['coordinates'] = {
#             'lat': data['coordinates'].split(',')[0],
#             'lng': data['coordinates'].split(',')[-1]
#         }
    
#     entity = stampedAPI.updateCustomEntity(authUserId, http_schema.entity_id, data)
#     entity = _convertHTTPEntity(entity, authClientId)
    
#     return transformOutput(entity.dataExport())


@handleHTTPRequest(http_schema=HTTPEntityId)
@require_http_methods(["POST"])
def remove(request, authUserId, authClientId, http_schema, **kwargs):
    entity = stampedAPI.removeCustomEntity(authUserId, http_schema.entity_id)
    entity = _convertHTTPEntity(entity, authClientId)

    return transformOutput(entity.dataExport())


@handleHTTPRequest(http_schema=HTTPEntitySearch, conversion=HTTPEntitySearch.exportEntitySearch)
@require_http_methods(["GET"])
def search(request, authUserId, schema, **kwargs):
    result = stampedAPI.searchEntities(authUserId=authUserId, 
                                       query=schema.q, 
                                       coords=schema.coordinates, 
                                       category=schema.category, 
                                       subcategory=schema.subcategory)
    
    autosuggest = []
    for item in result:
        try:
            item = HTTPEntityAutosuggest().importEntity(item[0], item[1]).dataExport()
            autosuggest.append(item)
        except Exception as e:
            logs.warning('HTTPEntityAutosuggest Import Error: %s (entity = %s)' % (e, item[1]))
    
    return transformOutput(autosuggest)


@handleHTTPRequest(http_schema=HTTPEntityNearby, conversion=HTTPEntityNearby.exportEntityNearby)
@require_http_methods(["GET"])
def nearby(request, authUserId, schema, **kwargs):
    result      = stampedAPI.searchNearby(authUserId=authUserId, 
                                          coords=schema.coordinates, 
                                          category=schema.category, 
                                          subcategory=schema.subcategory, 
                                          page=schema.page)
    
    autosuggest = []
    for item in result:
        item = HTTPEntityAutosuggest().importEntity(item[0], item[1]).dataExport()
        autosuggest.append(item)
    
    return transformOutput(autosuggest)


@handleHTTPRequest(http_schema=HTTPEntitySuggested, conversion=HTTPEntitySuggested.exportEntitySuggested)
@require_http_methods(["GET"])
def suggested(request, authUserId, schema, **kwargs):
    results     = stampedAPI.getSuggestedEntities(authUserId=authUserId, suggested=schema)
    convert     = lambda e: HTTPEntityAutosuggest().importEntity(e).dataExport()
    
    for section in results:
        section['entities'] = map(convert, section['entities'])
    
    return transformOutput(results)


@handleHTTPRequest(http_schema=HTTPEntityId)
@require_http_methods(["GET"])
def menu(request, authUserId, http_schema, **kwargs):
    menu        = stampedAPI.getMenu(http_schema.entity_id)
    http_menu   = HTTPMenu().importMenuSchema(menu)
    
    return transformOutput(http_menu.dataExport())


@handleHTTPRequest(requires_auth=False, http_schema=HTTPStampedBySlice)
@require_http_methods(["GET"])
def stampedBy(request, authUserId, http_schema, **kwargs):
    showCount   = True if http_schema.group is None else False
    
    result      = HTTPStampedBy()

    if http_schema.group is None:
        stampedby = stampedAPI.entityStampedBy(http_schema.entity_id, authUserId)
        result.importStampedBy(stampedby)

    elif http_schema.group == 'friends' and authUserId is not None:
        requestSlice = http_schema.exportFriendsSlice()
        requestSlice.distance = 1

        stamps, count = stampedAPI.getEntityStamps(http_schema.entity_id, authUserId, requestSlice, showCount)

        result.friends          = HTTPStampedByGroup()
        result.friends.stamps   = [HTTPStamp().importStamp(s) for s in stamps]
        if count is not None:
            result.friends.count = count

    elif http_schema.group == 'fof' and authUserId is not None:
        requestSlice = http_schema.exportFriendsSlice()
        requestSlice.distance = 2
        requestSlice.inclusive = False

        stamps, count = stampedAPI.getEntityStamps(http_schema.entity_id, authUserId, requestSlice, showCount)

        result.fof          = HTTPStampedByGroup()
        result.fof.stamps   = [HTTPStamp().importStamp(s) for s in stamps]
        if count is not None:
            result.fof.count = count

    elif http_schema.group == 'all':
        requestSlice  = http_schema.exportGenericCollectionSlice()
        stamps, count = stampedAPI.getEntityStamps(http_schema.entity_id, authUserId, requestSlice, showCount)

        result.all          = HTTPStampedByGroup()
        result.all.stamps   = [HTTPStamp().importStamp(s) for s in stamps]
        if count is not None:
            result.all.count = count
    
    return transformOutput(result.dataExport())


@handleHTTPRequest(http_schema=HTTPActionComplete)
@require_http_methods(["POST"])
def completeAction(request, http_schema, **kwargs):
    authUserId, authClientId = checkOAuth(request)
    
    #schema      = parseRequest(HTTPActionComplete(), request)
    logs.info('http_schema: %s' % http_schema)
    result      = stampedAPI.completeAction(authUserId, **http_schema.dataExport())

    return transformOutput(result)

