#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *


@handleHTTPRequest(http_schema=HTTPFavoriteNew)
@require_http_methods(["POST"])
def create(request, authUserId, http_schema, **kwargs):
    stampId     = http_schema.stamp_id
    entityRequest = {
        'entity_id': http_schema.entity_id,
        'search_id': http_schema.search_id,
    }
    
    favorite    = stampedAPI.addFavorite(authUserId, entityRequest, stampId)
    favorite    = HTTPFavorite().importSchema(favorite)
    
    return transformOutput(favorite.exportSparse())


@handleHTTPRequest(http_schema=HTTPEntityId)
@require_http_methods(["POST"])
def remove(request, authUserId, http_schema, **kwargs):
    favorite    = stampedAPI.removeFavorite(authUserId, http_schema.entity_id)
    favorite    = HTTPFavorite().importSchema(favorite)
    
    # Hack to force 'entity' to null for Bons
    ### TODO: Come up with a long-term solution
    result      = favorite.exportSparse()
    result['entity'] = None
    
    return transformOutput(result)


@handleHTTPRequest(http_schema=HTTPGenericCollectionSlice, schema=GenericCollectionSlice)
@require_http_methods(["GET"])
def show(request, authUserId, schema, **kwargs):
    favorites   = stampedAPI.getFavorites(authUserId, schema)
    
    result = []
    for favorite in favorites:
        result.append(HTTPFavorite().importSchema(favorite).exportSparse())
    
    return transformOutput(result)

