#!/u()sr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *


@handleHTTPRequest(http_schema=HTTPFavoriteNew)
@require_http_methods(["POST"])
def create(request, authUserId, http_schema, **kwargs):
    stampId  = http_schema.stamp_id
    entityRequest = {
        'entity_id': http_schema.entity_id,
        'search_id': http_schema.search_id,
    }

    favorite = stampedAPI.addFavorite(authUserId, entityRequest, stampId)
    favorite = HTTPFavorite().importFavorite(favorite)

    return transformOutput(favorite.dataExport())


@handleHTTPRequest(http_schema=HTTPEntityId)
@require_http_methods(["POST"])
def remove(request, authUserId, http_schema, **kwargs):
    favorite = stampedAPI.removeFavorite(authUserId, http_schema.entity_id)
    favorite = HTTPFavorite().importSchema(favorite)
    
    # Hack to force 'entity' to null for Bons
    ### TODO: Come up with a long-term solution
    result   = favorite.dataExport()
    result['entity'] = None
    
    return transformOutput(result)


@handleHTTPRequest(http_schema=HTTPGenericCollectionSlice,
                  conversion=HTTPGenericCollectionSlice.exportGenericCollectionSlice)
@require_http_methods(["GET"])
def show(request, authUserId, schema, **kwargs):
    favorites = stampedAPI.getFavorites(authUserId, schema)
    
    result = []
    for favorite in favorites:
        result.append(HTTPFavorite().importSchema(favorite).dataExport())
    
    return transformOutput(result)

