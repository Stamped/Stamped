#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from servers.httpapi.v0.helpers import *
from api.Schemas        import ClientLogsEntry

@handleHTTPRequest(http_schema=HTTPClientLogsEntry, conversion=HTTPClientLogsEntry.exportClientLogsEntry)
@require_http_methods(["POST"])
def create(request, authUserId, schema, **kwargs):
    result = stampedAPI.addClientLogsEntry(authUserId, schema)
    
    return transformOutput(True)

