#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import time, json
from django.http import HttpResponse

message = None
try:
    from httpapi.v0.helpers import *
    from resolve.EntitySearch   import EntitySearch
    from resolve.Resolver       import *
except Exception as e:
    message = str(e)

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

def searchDemo(request):
    try:
        kwargs = {}
        kwargs.setdefault('content_type', 'text/javascript; charset=UTF-8')
        kwargs.setdefault('mimetype', 'text/html')
        
        output = ''
        query = ''
        coord_string = ''
        if request.method == 'GET' and 'query' in request.GET:
            query = request.GET['query']
            coordinates = None
            if 'coordinates' in request.GET:
                coord_string = request.GET['coordinates']
                try:
                    pieces = coord_string.split(',')
                    if len(pieces) == 2:
                        coordinates = (float(pieces[0]),float(pieces[1]))
                except:
                    pass
            results = EntitySearch().search(query, coordinates=coordinates)

            output = formatResults(results, reverse=False)

        output_json = """
<html>
<head><title>Search Demo</title>
</head>
<body>
<form>
Coordinates (optional): <input type="text" name="coordinates" value="%s"/> (i.e. "43,-74.25")<br/>
Query String: <input type="text" name="query" value="%s"/>
<input type="submit" value="Submit" />
</form>
<pre>
%s
</pre>
</body>
</html>
        """ % ( coord_string, query, output )
        if message is not None:
            output_json += message
        response = HttpResponse(output_json, **kwargs)
        
        return response
    except Exception as e:
        print e
        response = HttpResponse("internal server error: %s" % e, status=500)
        return response
