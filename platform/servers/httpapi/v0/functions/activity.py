#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *

@handleHTTPRequest(http_schema=HTTPActivitySlice)
@require_http_methods(["GET"])
def show(request, authUserId, data, **kwargs):
    data['distance'] = 0

    # Hack for python < 2.6.5 (doesn't support unicode as keyword args?!?)
    newData = {}
    for k, v in data.items():
        newData[str(k)] = v

    activity = stampedAPI.getActivity(authUserId, **newData)
    
    result = []
    for item in activity:
        result.append(HTTPActivity().importEnrichedActivity(item).dataExport())
    
    return transformOutput(result)

@handleHTTPRequest(http_schema=HTTPActivitySlice)
@require_http_methods(["GET"])
def friends(request, authUserId, data, **kwargs):
    data['distance'] = 1

    # Hack for python < 2.6.5 (doesn't support unicode as keyword args?!?)
    newData = {}
    for k, v in data.items():
        newData[str(k)] = v

    activity = stampedAPI.getActivity(authUserId, **newData)
    
    result = []
    for item in activity:
        result.append(HTTPActivity().importEnrichedActivity(item).dataExport())
    
    return transformOutput(result)

@handleHTTPRequest()
@require_http_methods(["GET"])
def unread(request, authUserId, **kwargs):
    count   = stampedAPI.getUnreadActivityCount(authUserId)
    return transformOutput({'num_unread': count})

