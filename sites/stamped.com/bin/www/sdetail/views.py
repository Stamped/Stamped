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

stampedAPI  = MongoStampedAPI()


def show(request, **kwargs):

    stampId = kwargs.pop('stamp_id', None)
    try:
        stamp = stampedAPI.getStamp(stampId)
        # stamp['credit'] = stamp['credit'][:1]
        return render_to_response('sdetail.html', stamp)
    except:
        raise Http404
    #     return HttpResponse("Whoa that's messed up")

    """
    URL Regex:
    name = name.lower().replace(' ', '_').encode('ascii', 'ignore')
    name = re.sub('([^a-zA-Z0-9._-])', '', name)
    """