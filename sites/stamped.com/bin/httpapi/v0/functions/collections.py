#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from httpapi.v0.helpers import *

@handleHTTPRequest
@require_http_methods(["GET"])
def inbox(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPGenericSlice(), request)
    
    data        = schema.exportSparse()
    stamps      = stampedAPI.getInboxStamps(authUserId, **data)
    
    result = []
    for stamp in stamps:
        if 'deleted' in stamp:
            result.append(HTTPDeletedStamp().importSchema(stamp).exportSparse())
        else:
            result.append(HTTPStamp().importSchema(stamp).exportSparse())
    
    return transformOutput(result)


@handleHTTPRequest
@require_http_methods(["GET"])
def user(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserCollectionSlice(), request)
    
    data        = schema.exportSparse()
    userRequest = {
                    'user_id':      data.pop('user_id', None),
                    'screen_name':  data.pop('screen_name', None)
                  }
    stamps      = stampedAPI.getUserStamps(userRequest, authUserId, **data)
    
    result = []
    for stamp in stamps:
        if 'deleted' in stamp:
            result.append(HTTPDeletedStamp().importSchema(stamp).exportSparse())
        else:
            result.append(HTTPStamp().importSchema(stamp).exportSparse())
    
    return transformOutput(result)


@handleHTTPRequest
@require_http_methods(["GET"])
def credit(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPUserCollectionSlice(), request)
    
    data        = schema.exportSparse()
    userRequest = {
                    'user_id':      data.pop('user_id', None),
                    'screen_name':  data.pop('screen_name', None)
                  }
    stamps      = stampedAPI.getCreditedStamps(userRequest, authUserId, **data)
    
    result = []
    for stamp in stamps:
        if 'deleted' in stamp:
            result.append(HTTPDeletedStamp().importSchema(stamp).exportSparse())
        else:
            result.append(HTTPStamp().importSchema(stamp).exportSparse())
    
    return transformOutput(result)

