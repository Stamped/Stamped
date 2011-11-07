#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import init

from django.http import HttpResponse, Http404, HttpResponseRedirect
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

def terms(request):
    try:
        response = render_to_response('terms-mobile.html', None)

        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response
    except:
        raise Http404

def privacy(request):
    try:
        response = render_to_response('privacy-mobile.html', None)

        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response
    except:
        raise Http404

def feedback(request):
    try:
        response = render_to_response('feedback-mobile.html', None)

        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response
    except:
        raise Http404

def download(request):
    return HttpResponseRedirect('http://www.itunes.com')
    
