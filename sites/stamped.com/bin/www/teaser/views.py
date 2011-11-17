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
        autoplay_video = bool(request.GET.get('video', False))

        response = render_to_response('index.html', {'autoplay_video': autoplay_video})

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

def licenses(request):
    try:
        response = render_to_response('licenses-mobile.html', None)

        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response
    except:
        raise Http404

def faq(request):
    try:
        response = render_to_response('faq-mobile.html', None)

        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response
    except:
        raise Http404

def download(request):
    return HttpResponseRedirect('http://itunes.apple.com/us/app/stamped/id467924760?ls=1&mt=8')

