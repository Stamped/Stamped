# Create your views here.
#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import os, utils, json, random, time, hashlib, logs, traceback, string

from datetime           import *
from errors             import *
from HTTPSchemas        import *
from MongoStampedAPI    import MongoStampedAPI
from django.http        import HttpResponse, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts   import render_to_response

stampedAPI  = MongoStampedAPI()


### WEBSITE

def sxsw(request):
    try:
        response = render_to_response('sxsw.html', None)
        
        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'
        
        return response
    except:
        raise Http404

def test(request):
    try:
        response = render_to_response('test.html', None)
        
        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'
        
        return response
    except:
        raise Http404


### JSON

def _transformOutput(value, **kwargs):
    kwargs.setdefault('content_type', 'text/javascript; charset=UTF-8')
    kwargs.setdefault('mimetype', 'application/json')

    output_json = json.dumps(value, sort_keys=True)
    output = HttpResponse(output_json, **kwargs)
        
    output['Expires'] = (datetime.utcnow() + timedelta(minutes=10)).ctime()
    output['Cache-Control'] = 'max-age=600'
    
    # pretty_output = json.dumps(value, sort_keys=True, indent=2)
    # logs.output(output_json)

    return output

def _transformStamps(stamps):
    result = []
    for stamp in stamps:
        try:
            if 'deleted' in stamp:
                result.append(HTTPDeletedStamp().importSchema(stamp).exportSparse())
            else:
                result.append(HTTPStamp().importSchema(stamp).exportSparse())
        except:
            logs.warn(utils.getFormattedException())
    
    return result

def sxsw_json(request):
    try:
        uSlice = UserCollectionSlice()
        uSlice.limit = 100
        uSlice.screen_name = 'kevin'

        stamps = stampedAPI.getUserStamps('4e570489ccc2175fcd000000', uSlice)
        
        return _transformOutput(_transformStamps(stamps))

    except Exception as e:
        logs.warning(e)
        raise Http404

