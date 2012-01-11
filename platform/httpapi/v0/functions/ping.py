#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import time, json
from django.http import HttpResponse

def ping(request):
    try:
        kwargs = {}
        kwargs.setdefault('content_type', 'text/javascript; charset=UTF-8')
        kwargs.setdefault('mimetype', 'application/json')
        
        output_json = json.dumps(True)
        response = HttpResponse(output_json, **kwargs)
        
        return response
    except Exception as e:
        print e
        response = HttpResponse("internal server error", status=500)
        return response
