#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *


@handleHTTPRequest(http_schema=HTTPActivitySlice)
@require_http_methods(["GET"])
def collection(request, authUserId, http_schema, **kwargs):
    import time

    activity = stampedAPI.getActivity(authUserId, http_schema.scope, limit=http_schema.limit, offset=http_schema.offset)

    t0 = time.time()
    t1 = t0
    totalTime = 0
    result = []
    for item in activity:
        t1 = time.time()
        result.append(HTTPActivity().importEnrichedActivity(item).dataExport())
        logs.debug('time for importEnrichedActivity: %s' % (time.time() - t1))
        totalTime += float(t1)
    logs.debug('TOTAL time for importEnrichedActivity loop: %s' % (time.time() - t0))
    logs.debug("### aggregated time: %s" % totalTime)
    return transformOutput(result)

@handleHTTPRequest()
@require_http_methods(["GET"])
def unread(request, authUserId, **kwargs):
    count   = stampedAPI.getUnreadActivityCount(authUserId)
    return transformOutput({'num_unread': count})

