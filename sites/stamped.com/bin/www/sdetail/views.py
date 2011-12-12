#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals
import os, json, utils, random, time, hashlib, logs
import datetime

from errors             import *
from HTTPSchemas        import *
from MongoStampedAPI    import MongoStampedAPI
from django.http        import HttpResponse, Http404
from django.shortcuts   import render_to_response

stampedAPI  = MongoStampedAPI()

def show(request, **kwargs):
    screenName  = kwargs.pop('screen_name', None)
    stampNum    = kwargs.pop('stamp_num', None)
    stampTitle  = kwargs.pop('stamp_title', None)
    mobile      = kwargs.pop('mobile', False)

    try:
        stamp = stampedAPI.getStampFromUser(screenName, stampNum)

        template = 'sdetail.html'
        if mobile:
            template = 'sdetail-mobile.html'

        encodedStampTitle = encodeStampTitle(stamp.entity.title)
        
        if encodedStampTitle != stampTitle:
            i = encodedStampTitle.find('.')
            if i != -1:
                encodedStampTitle = encodedStampTitle[:i]
            
            if encodedStampTitle != stampTitle:
                raise Exception("invalid stamp title: '%s' vs '%s'" % (stampTitle, encodedStampTitle))

        params = HTTPStamp().importSchema(stamp).value
        params['image_url_92'] = params['user']['image_url'].replace('.jpg', '-92x92.jpg')

        response = render_to_response(template, params)
        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response

    except Exception as e:
        logs.begin()
        logs.request(request)
        logs.warning("500 Error: %s" % e)
        logs.error(500)
        raise Http404

def mobile(request, **kwargs):
    kwargs['mobile'] = True
    return show(request, **kwargs)
