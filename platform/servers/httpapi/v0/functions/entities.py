#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *

def _convertHTTPEntity(entity, authClientId=None):
    client = stampedAuth.getClientDetails(authClientId)
    
    if client.api_version < 1:
        return HTTPEntity_stampedtest().importSchema(entity)
    else:
        return HTTPEntity().importEntity(entity, client)


@handleHTTPRequest(http_schema=HTTPEntityNew)
@require_http_methods(["POST"])
def create(request, authUserId, authClientId, http_schema, **kwargs):
    entity          = http_schema.exportEntity(authUserId)
    
    entity          = stampedAPI.addEntity(entity)
    entity          = _convertHTTPEntity(entity, authClientId)
    
    return transformOutput(entity.exportSparse())


@handleHTTPRequest(requires_auth=False, http_schema=HTTPEntityIdSearchId)
@require_http_methods(["GET"])
def show(request, authUserId, authClientId, http_schema, **kwargs):
    entity      = stampedAPI.getEntity(http_schema, authUserId)
    entity      = _convertHTTPEntity(entity, authClientId)
    
    return transformOutput(entity.exportSparse())

@handleHTTPRequest(http_schema=HTTPEntityEdit)
@require_http_methods(["POST"])
def update(request, authUserId, authClientId, http_schema, data, **kwargs):
    ### TEMP: Generate list of changes. Need to do something better eventually...
    del(data['entity_id'])
    
    for k, v in data.iteritems():
        if v == '':
            data[k] = None
    if 'address' in data:
        data['details.place.address'] = data['address']
        del(data['address'])
    if 'coordinates' in data and data['coordinates'] != None:
        data['coordinates'] = {
            'lat': data['coordinates'].split(',')[0],
            'lng': data['coordinates'].split(',')[-1]
        }
    
    entity = stampedAPI.updateCustomEntity(authUserId, http_schema.entity_id, data)
    entity = _convertHTTPEntity(entity, authClientId)
    
    return transformOutput(entity.exportSparse())


@handleHTTPRequest(http_schema=HTTPEntityId)
@require_http_methods(["POST"])
def remove(request, authUserId, authClientId, http_schema, **kwargs):
    entity = stampedAPI.removeCustomEntity(authUserId, http_schema.entity_id)
    entity = _convertHTTPEntity(entity, authClientId)

    return transformOutput(entity.exportSparse())


@handleHTTPRequest(http_schema=HTTPEntitySearch, schema=EntitySearch)
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
            item = HTTPEntityAutosuggest().importSchema(item[0], item[1]).exportSparse()
            autosuggest.append(item)
        except Exception as e:
            logs.warning('Error: %s\n%s' % (e, item[1]))
    
    return transformOutput(autosuggest)


@handleHTTPRequest(http_schema=HTTPEntityNearby, schema=EntityNearby)
@require_http_methods(["GET"])
def nearby(request, authUserId, schema, **kwargs):
    result      = stampedAPI.searchNearby(authUserId=authUserId, 
                                          coords=schema.coordinates, 
                                          category=schema.category, 
                                          subcategory=schema.subcategory, 
                                          page=schema.page)
    
    autosuggest = []
    for item in result:
        item = HTTPEntityAutosuggest().importSchema(item[0], item[1]).exportSparse()
        autosuggest.append(item)
    
    return transformOutput(autosuggest)


@handleHTTPRequest(http_schema=HTTPEntitySuggested, schema=EntitySuggested)
@require_http_methods(["GET"])
def suggested(request, authUserId, schema, **kwargs):
    results     = stampedAPI.getSuggestedEntities(authUserId=authUserId, suggested=schema)
    convert     = lambda e: HTTPEntityAutosuggest().importSchema(e).exportSparse()
    
    for section in results:
        section['entities'] = map(convert, section['entities'])
    
    return transformOutput(results)


@handleHTTPRequest(http_schema=HTTPEntityId)
@require_http_methods(["GET"])
def menu(request, authUserId, http_schema, **kwargs):
    menu        = stampedAPI.getMenu(http_schema.entity_id)
    http_menu   = HTTPMenu().importSchema(menu)
    
    return transformOutput(http_menu.exportSparse())


@handleHTTPRequest(requires_auth=False, http_schema=HTTPStampedBySlice)
@require_http_methods(["GET"])
def stampedBy(request, authUserId, http_schema, **kwargs):
    showCount   = True if http_schema.group is None else False
    
    result      = HTTPStampedBy()

    if authUserId is not None:
        if http_schema.group is None or http_schema.group == 'friends':
            requestSlice = http_schema.exportSchema(FriendsSlice())
            requestSlice.distance = 1

            stamps, count = stampedAPI.getEntityStamps(http_schema.entity_id, authUserId, requestSlice, showCount)

            for stamp in stamps:
                result.friends.stamps.append(HTTPStamp().importSchema(stamp).exportSparse())
            if count is not None:
                result.friends.count = count

        if http_schema.group is None or http_schema.group == 'fof':
            requestSlice = http_schema.exportSchema(FriendsSlice())
            requestSlice.distance = 2
            requestSlice.inclusive = False

            stamps, count = stampedAPI.getEntityStamps(http_schema.entity_id, authUserId, requestSlice, showCount)

            for stamp in stamps:
                result.fof.stamps.append(HTTPStamp().importSchema(stamp).exportSparse())
            if count is not None:
                result.fof.count = count
    
    if http_schema.group is None or http_schema.group == 'all':
        requestSlice  = http_schema.exportSchema(GenericCollectionSlice())
        stamps, count = stampedAPI.getEntityStamps(http_schema.entity_id, authUserId, requestSlice, showCount)
        
        for stamp in stamps:
            result.all.stamps.append(HTTPStamp().importSchema(stamp).exportSparse())
        if count is not None:
            result.all.count = count
    
    return transformOutput(result.exportSparse())


@handleHTTPRequest(http_schema=HTTPActionComplete)
@require_http_methods(["POST"])
def completeAction(request, http_schema, **kwargs):
    authUserId, authClientId = checkOAuth(request)
    
    #schema      = parseRequest(HTTPActionComplete(), request)
    logs.info('http_schema.value: %s' % http_schema.value)
    result      = stampedAPI.completeAction(authUserId, **http_schema.value)

    return transformOutput(result)

