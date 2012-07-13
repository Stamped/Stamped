#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from servers.httpapi.v0.helpers import *

exceptions = [
    (StampedInvalidUniversalNewsItemError, 400, "bad_request", "There was an error adding the activity item."),
]

@handleHTTPRequest(http_schema=HTTPActivitySlice,
                   exceptions=exceptions)
@require_http_methods(["GET"])
def collection(request, authUserId, http_schema, **kwargs):
    import time

    activity = stampedAPI.getActivity(authUserId, http_schema.scope, limit=http_schema.limit, offset=http_schema.offset)

    result = []
    t0 = time.time()
    for item in activity:
        try:
            result.append(HTTPActivity().importEnrichedActivity(item).dataExport())
        except Exception as e:
            logs.warning("Failed to enrich activity: %s" % e)
            logs.debug("Activity: %s" % item)
    return transformOutput(result)

@handleHTTPRequest(exceptions=exceptions)
@require_http_methods(["GET"])
def unread(request, authUserId, **kwargs):
    count   = stampedAPI.getUnreadActivityCount(authUserId)
    return transformOutput({'num_unread': count})

