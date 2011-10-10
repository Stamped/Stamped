#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import init
import os, json, utils, random, time, hashlib, logs

from errors import *
from api.HTTPSchemas import *
from api.MongoStampedAPI import MongoStampedAPI
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
import datetime

stampedAPI  = MongoStampedAPI()

def show(request, **kwargs):
    screenName  = kwargs.pop('screen_name', None)
    stampNum    = kwargs.pop('stamp_num', None)
    stampTitle  = kwargs.pop('stamp_title', None)
    mobile      = kwargs.pop('mobile', False)

    try:
        stamp = stampedAPI.getStampFromUser(screenName, stampNum)

        # stamp['credit'] = stamp['credit'][:1]
        template = 'sdetail.html'
        if mobile:
            template = 'sdetail-mobile.html'

        if encodeStampTitle(stamp.entity.title) != stampTitle:
            raise

        response = render_to_response(template, stamp)
        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response

    except:
        logs.begin(stampedAPI._logsDB.addLog)
        logs.request(request)
        logs.error(500)
        raise Http404

def mobile(request, **kwargs):
    kwargs['mobile'] = True
    return show(request, **kwargs)
