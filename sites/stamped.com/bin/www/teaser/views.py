#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import init

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
import datetime

def about(request):
    try:
        response = render_to_response('about.html', None)

        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response
    except:
        raise Http404

def index(request):
    try:
        response = render_to_response('index.html', None)

        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response
    except:
        raise Http404
    