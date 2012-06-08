#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *

@handleHTTPRequest(http_schema=HTTPActivitySlice)
@require_http_methods(["GET"])
def show(request, authUserId, http_schema, **kwargs):
    actSlice = http_schema.exportActivitySlice()
    actSlice.distance = 0
    activity = stampedAPI.getActivity(authUserId, actSlice)

    result = []
    for item in activity:
        result.append(HTTPActivity().importEnrichedActivity(item).dataExport())
    
    return transformOutput(result)

@handleHTTPRequest(http_schema=HTTPActivitySlice)
@require_http_methods(["GET"])
def friends(request, authUserId, http_schema, **kwargs):
    actSlice = http_schema.exportActivitySlice()
    actSlice.distance = 1
    activity = stampedAPI.getActivity(authUserId, actSlice)
    
    result = []
    for item in activity:
        result.append(HTTPActivity().importEnrichedActivity(item).dataExport())
    
    return transformOutput(result)

@handleHTTPRequest()
@require_http_methods(["GET"])
def unread(request, authUserId, **kwargs):
    count   = stampedAPI.getUnreadActivityCount(authUserId)
    return transformOutput({'num_unread': count})

