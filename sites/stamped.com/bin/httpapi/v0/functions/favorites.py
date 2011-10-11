#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *


@handleHTTPRequest
@require_http_methods(["POST"])
def create(request):
    authUserId  = checkOAuth(request)

    schema      = parseRequest(HTTPFavoriteNew(), request)
    entityId    = schema.entity_id
    stampId     = schema.stamp_id

    favorite    = stampedAPI.addFavorite(authUserId, entityId, stampId)
    favorite    = HTTPFavorite().importSchema(favorite)

    return transformOutput(favorite.exportSparse())


@handleHTTPRequest
@require_http_methods(["POST"])
def remove(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPEntityId(), request)

    favorite    = stampedAPI.removeFavorite(authUserId, schema.entity_id)
    favorite    = HTTPFavorite().importSchema(favorite)

    # Hack to force 'entity' to null for Bons
    ### TODO: Come up with a long-term solution
    result      = favorite.exportSparse()
    result['entity'] = None

    return transformOutput(result)


@handleHTTPRequest
@require_http_methods(["GET"])
def show(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPGenericSlice(), request)

    favorites   = stampedAPI.getFavorites(authUserId, **schema.exportSparse())

    result = []
    for favorite in favorites:
        result.append(HTTPFavorite().importSchema(favorite).exportSparse())
    
    return transformOutput(result)


