#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *

def transform_stamps(stamps):
    result = []
    for stamp in stamps:
        if 'deleted' in stamp:
            result.append(HTTPDeletedStamp().importSchema(stamp).exportSparse())
        else:
            result.append(HTTPStamp().importSchema(stamp).exportSparse())
    
    return result

@handleHTTPRequest
@require_http_methods(["GET"])
def inbox(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPGenericSlice(), request).exportSchema(GenericSlice())
    stamps      = stampedAPI.getInboxStamps(authUserId, schema)
    
    return transformOutput(transform_stamps(stamps))

@handleHTTPRequest
@require_http_methods(["GET"])
def user(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserCollectionSlice(), request).exportSchema(UserCollectionSlice())
    stamps      = stampedAPI.getUserStamps(authUserId, schema)
    
    return transformOutput(transform_stamps(stamps))

@handleHTTPRequest
@require_http_methods(["GET"])
def credit(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserCollectionSlice(), request).exportSchema(UserCollectionSlice())
    stamps      = stampedAPI.getCreditedStamps(authUserId, schema)
    
    return transformOutput(transform_stamps(stamps))

@handleHTTPRequest
@require_http_methods(["GET"])
def friends(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPFriendsSlice(), request).exportSchema(FriendsSlice())
    stamps      = stampedAPI.getFriendsStamps(authUserId, schema)
    
    return transformOutput(transform_stamps(stamps))


