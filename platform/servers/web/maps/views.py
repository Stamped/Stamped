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
from api_old.HTTPSchemas        import *
from api_old.MongoStampedAPI    import MongoStampedAPI
from django.http        import HttpResponse, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts   import render_to_response

stampedAPI  = MongoStampedAPI()


### WEBSITE

def test(request):
    try:
        response = render_to_response('test.html', None)
        
        response['Expires'] = (datetime.utcnow() + timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'
        
        return response
    except:
        raise Http404

def sxsw(request):
    template = 'sxsw.html'

    try:
        cSlice = GenericCollectionSlice()
        cSlice.limit = 100

        cSlice.sort = 'relevance'
        cSlice.unique = True
        cSlice.quality = 1
        cSlice.viewport.upper_left.lat   = 30.309242
        cSlice.viewport.upper_left.lng   = -97.792286
        cSlice.viewport.lower_right.lat  = 30.226775
        cSlice.viewport.lower_Right.lng  = -97.697689

        stamps = stampedAPI.getSuggestedStamps(None, cSlice)
        
        return _buildMap(template, stamps)
    except:
        raise Http404

def user(request, **kwargs):
    screenName  = kwargs.pop('screen_name', None)
    template = 'maps.html'

    try:
        uSlice = UserCollectionSlice()
        uSlice.screen_name = screenName
        uSlice.quality = 1
        uSlice.sort = 'relevance'

        stamps = stampedAPI.getUserStamps(None, uSlice)
        
        return _buildMap(template, stamps)
    except:
        raise Http404


### PRIVATE

def _buildMap(template, stamps):
    try:
        result = []

        for stamp in stamps:
            try:
                if 'deleted' not in stamp:
                    result.append(HTTPStamp().importSchema(stamp).dataExport())
            except:
                logs.warn(utils.getFormattedException())

        result = json.dumps(result, sort_keys=True)

        response = render_to_response(template, {'stamps': result})
        response['Expires'] = (datetime.utcnow() + timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'
        
        return response

    except Exception as e:
        logs.warning("Error: %s" % e)
        raise Http404

