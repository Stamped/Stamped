#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *

@handleHTTPRequest(requires_auth=False)
@require_http_methods(["GET", "POST"])
def ping(request, **kwargs):
    # logs.info("HERE")
    return transformOutput(True)

