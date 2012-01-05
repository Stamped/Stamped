#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__   = "TODO"

import Globals
import os, json, utils, random, time, hashlib, logs

from datetime           import *
from errors             import *
from HTTPSchemas        import *
from MongoStampedAPI    import MongoStampedAPI
from django.http        import HttpResponse, Http404
from django.shortcuts   import render_to_response

stampedAPI  = MongoStampedAPI()

def formatDuration(length):
    try:
        hours = math.floor(length / 60.0 / 60.0)
        if hours > 0:
            minutes = math.floor(length % (hours * 60.0 * 60.0) / 60.0)
            result = "%i hr %i min" % (int(hours), int(minutes))
        else:
            minutes = math.floor(length / 60.0)
            result = "%i min" % int(minutes)
        return result
    except:
        return None


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

        entity = stampedAPI.getEntity({'entity_id': stamp.entity_id})
        opentable_url = None
        if entity.rid is not None:
            opentable_url = "http://www.opentable.com/single.aspx?rid=%s&ref=9166" % entity.rid
        entity = HTTPEntity().importSchema(entity)
        if entity.opentable_url and opentable_url is not None:
            entity.opentable_url = opentable_url

        params = HTTPStamp().importSchema(stamp).value
        params['entity'] = entity.value

        if entity.genre == 'film' and entity.length:
            params['entity']['duration'] = formatDuration(entity.length)
        params['image_url_92'] = params['user']['image_url'].replace('.jpg', '-92x92.jpg')

        response = render_to_response(template, params)
        response['Expires'] = (datetime.utcnow() + timedelta(minutes=10)).ctime()
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
