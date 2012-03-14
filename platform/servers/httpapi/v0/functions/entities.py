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
        return HTTPEntity().importSchema(entity, client)


@handleHTTPRequest
@require_http_methods(["POST"])
def create(request):
    authUserId, authClientId = checkOAuth(request)
    
    schema      = parseRequest(HTTPEntityNew(), request)
    entity      = schema.exportSchema(Entity())

    entity.generated_by = authUserId
    
    entity      = stampedAPI.addEntity(entity)
    entity      = _convertHTTPEntity(entity, authClientId)

    return transformOutput(entity.exportSparse())


@handleHTTPRequest
@require_http_methods(["GET"])
def show(request):
    authUserId, authClientId = checkOAuth(request)

    schema      = parseRequest(HTTPEntityIdSearchId(), request)
    entity      = stampedAPI.getEntity(schema, authUserId)
    entity      = _convertHTTPEntity(entity, authClientId)

    return transformOutput(entity.exportSparse())

@handleHTTPRequest
@require_http_methods(["POST"])
def update(request):
    authUserId, authClientId = checkOAuth(request)
    
    schema      = parseRequest(HTTPEntityEdit(), request)

    ### TEMP: Generate list of changes. Need to do something better eventually...
    data        = schema.exportSparse()
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
    
    entity      = stampedAPI.updateCustomEntity(authUserId, schema.entity_id, data)
    entity      = _convertHTTPEntity(entity, authClientId)

    return transformOutput(entity.exportSparse())


@handleHTTPRequest
@require_http_methods(["POST"])
def remove(request):
    authUserId, authClientId = checkOAuth(request)
    
    schema      = parseRequest(HTTPEntityId(), request)
    entity      = stampedAPI.removeCustomEntity(authUserId, schema.entity_id)
    entity      = _convertHTTPEntity(entity, authClientId)

    return transformOutput(entity.exportSparse())


@handleHTTPRequest
@require_http_methods(["GET"])
def search(request):
    authUserId, authClientId = checkOAuth(request)
    
    schema      = parseRequest(HTTPEntitySearch(), request)
    search      = schema.exportSchema(EntitySearch())
    
    result      = stampedAPI.searchEntities(query=search.q, 
                                            coords=search.coordinates, 
                                            authUserId=authUserId, 
                                            category_filter=search.category, 
                                            subcategory_filter=search.subcategory, 
                                            local=search.local, 
                                            page=search.page)
    
    autosuggest = []
    for item in result:
        item = HTTPEntityAutosuggest().importSchema(item[0], item[1]).exportSparse()
        autosuggest.append(item)
    
    return transformOutput(autosuggest)


@handleHTTPRequest
@require_http_methods(["GET"])
def nearby(request):
    authUserId, authClientId = checkOAuth(request)
    
    schema      = parseRequest(HTTPEntityNearby(), request)
    search      = schema.exportSchema(EntityNearby())
    
    result      = stampedAPI.searchNearby(coords=search.coordinates, 
                                          authUserId=authUserId, 
                                          category_filter=search.category, 
                                          subcategory_filter=search.subcategory, 
                                          page=search.page)
    
    autosuggest = []
    for item in result:
        item = HTTPEntityAutosuggest().importSchema(item[0], item[1]).exportSparse()
        autosuggest.append(item)
    
    return transformOutput(autosuggest)


@handleHTTPRequest
@require_http_methods(["GET"])
def menu(request):
    authUserId, authClientId = checkOAuth(request)
    
    schema      = parseRequest(HTTPEntityId(), request)
    menu        = stampedAPI.getMenu(schema.entity_id)
    httpMenu    = HTTPMenu().importSchema(menu)
    return transformOutput(httpMenu.exportSparse())


@handleHTTPRequest
@require_http_methods(["GET"])
def stampedBy(request):
    authUserId, authClientId = checkOAuth(request)
    
    schema      = parseRequest(HTTPStampedBySlice(), request)
    showCount   = True if schema.group is None else False

    result      = HTTPStampedBy()

    if schema.group is None or schema.group == 'friends':
        requestSlice = schema.exportSchema(FriendsSlice())
        requestSlice.distance = 1
        stamps, count = stampedAPI.getEntityStamps(schema.entity_id, authUserId, requestSlice, showCount)
        for stamp in stamps:
            result.friends.stamps.append(HTTPStamp().importSchema(stamp).exportSparse())
        if count is not None:
            result.friends.count = count

    if schema.group is None or schema.group == 'fof':
        requestSlice = schema.exportSchema(FriendsSlice())
        requestSlice.distance = 2
        import sys
        logs.info(sys.modules)
        logs.info("ID: %s" % id(FriendsSlice))
        logs.info("SCHEMA ID: %s" % id(Schema))
        logs.info('FRIENDSSLICE: %s' % isinstance(requestSlice, FriendsSlice))
        logs.info('GENERIC: %s' % isinstance(requestSlice, GenericCollectionSlice))
        stamps, count = stampedAPI.getEntityStamps(schema.entity_id, authUserId, requestSlice, showCount)
        for stamp in stamps:
            result.fof.stamps.append(HTTPStamp().importSchema(stamp).exportSparse())
        if count is not None:
            result.fof.count = count

    if schema.group is None or schema.group == 'all':
        requestSlice = schema.exportSchema(GenericCollectionSlice())
        stamps, count = stampedAPI.getEntityStamps(schema.entity_id, authUserId, requestSlice, showCount)
        for stamp in stamps:
            result.all.stamps.append(HTTPStamp().importSchema(stamp).exportSparse())
        if count is not None:
            result.all.count = count

    return transformOutput(result.exportSparse())


