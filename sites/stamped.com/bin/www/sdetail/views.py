#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import init
import os, json, utils, random, time, hashlib, logs

from errors import *
from HTTPSchemas import *
from api.MongoStampedAPI import MongoStampedAPI
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from plugins.minidetector import detect_mobile

stampedAPI  = MongoStampedAPI()

@detect_mobile
def show(request, **kwargs):
    screenName = kwargs.pop('screen_name', None)
    stampNum = kwargs.pop('stamp_num', None)
    try:
        stamp = stampedAPI.getStampFromUser(screenName, stampNum)
        # stamp['credit'] = stamp['credit'][:1]
        template = 'sdetail.html'
        if request.mobile:
            template = 'sdetail-mobile.html'
        return render_to_response(template, stamp)
    except:
        raise Http404
    #     return HttpResponse("Whoa that's messed up")

def mobile(request, **kwargs):

    screenName = kwargs.pop('screen_name', None)
    stampNum = kwargs.pop('stamp_num', None)
    try:
        stamp = stampedAPI.getStampFromUser(screenName, stampNum)
        # stamp['credit'] = stamp['credit'][:1]
        return render_to_response('sdetail-mobile.html', stamp)
    except:
        raise Http404
    #     return HttpResponse("Whoa that's messed up")
