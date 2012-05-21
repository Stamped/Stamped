#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *
import time

@handleHTTPRequest()
@require_http_methods(["GET"])
def timeout(request, authUserId, **kwargs):
    schema = parseRequest(None, request)
    
    time.sleep(55)

