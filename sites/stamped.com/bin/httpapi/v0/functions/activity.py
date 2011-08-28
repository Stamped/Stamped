#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from httpapi.v0.helpers import *

@handleHTTPRequest
@require_http_methods(["GET"])
def show(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPGenericSlice(), request)

    activity    = stampedAPI.getActivity(authUserId, **schema.exportSparse())
    
    result = []
    for item in activity:
        result.append(HTTPActivity().importSchema(item).exportSparse())

    return transformOutput(result)



