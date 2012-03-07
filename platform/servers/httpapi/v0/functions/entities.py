#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *

def _convertHTTPEntity(entity, clientId=None):
    if clientId == 'stampedtest':
        logs.info('STAMPED TEST!!!')
        return HTTPEntity_stampedtest().importSchema(entity)
    else:
        return HTTPEntity().importSchema(entity)


@handleHTTPRequest
@require_http_methods(["POST"])
def create(request):
    authUserId, clientId = checkOAuth(request)
    
    schema      = parseRequest(HTTPEntityNew(), request)
    entity      = schema.exportSchema(Entity())

    entity.generated_by = authUserId
    
    entity      = stampedAPI.addEntity(entity)
    entity      = _convertHTTPEntity(entity, clientId)

    return transformOutput(entity.exportSparse())


@handleHTTPRequest
@require_http_methods(["GET"])
def show(request):
    authUserId, clientId = checkOAuth(request)

    schema      = parseRequest(HTTPEntityIdSearchId(), request)
    entity      = stampedAPI.getEntity(schema, authUserId)
    entity      = _convertHTTPEntity(entity, clientId)

    return transformOutput(entity.exportSparse())

@handleHTTPRequest
@require_http_methods(["POST"])
def update(request):
    authUserId, clientId = checkOAuth(request)
    
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
    entity      = _convertHTTPEntity(entity, clientId)

    return transformOutput(entity.exportSparse())


@handleHTTPRequest
@require_http_methods(["POST"])
def remove(request):
    authUserId, clientId = checkOAuth(request)
    
    schema      = parseRequest(HTTPEntityId(), request)
    entity      = stampedAPI.removeCustomEntity(authUserId, schema.entity_id)
    entity      = _convertHTTPEntity(entity, clientId)

    return transformOutput(entity.exportSparse())


@handleHTTPRequest
@require_http_methods(["GET"])
def search(request):
    authUserId, clientId = checkOAuth(request)
    
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
    authUserId, clientId = checkOAuth(request)
    
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
    authUserId, clientId = checkOAuth(request)
    
    schema      = parseRequest(HTTPEntityId(), request)
    menu        = stampedAPI.getMenu(schema.entity_id)
    httpMenu    = HTTPMenu().importSchema(menu)
    return transformOutput(httpMenu.exportSparse())


