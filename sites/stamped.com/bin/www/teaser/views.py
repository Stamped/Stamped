#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import init

from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render_to_response
import datetime


### WEBSITE

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

def faq(request):
    try:
        response = render_to_response('faq.html', None)

        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response
    except:
        raise Http404

def privacy(request):
    try:
        response = render_to_response('privacy.html', None)

        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response
    except:
        raise Http404

def terms(request):
    try:
        response = render_to_response('terms.html', None)

        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response
    except:
        raise Http404

def download(request):
    response = render_to_response('redirect.html', None)
    response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
    response['Cache-Control'] = 'max-age=600'
    
    return response
    return HttpResponsePermanentRedirect('http://itunes.apple.com/us/app/stamped/id467924760?ls=1&mt=8')



### TEMP


def aboutOld(request):
    try:
        response = render_to_response('about_old.html', None)

        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response
    except:
        raise Http404

def indexOld(request):
    try:
        response = render_to_response('index_old.html', None)

        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response
    except:
        raise Http404


### MOBILE

def mobileTerms(request):
    try:
        response = render_to_response('terms-mobile.html', None)

        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response
    except:
        raise Http404

def mobilePrivacy(request):
    try:
        response = render_to_response('privacy-mobile.html', None)

        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response
    except:
        raise Http404

def mobileFeedback(request):
    try:
        response = render_to_response('feedback-mobile.html', None)

        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response
    except:
        raise Http404

def mobileLicenses(request):
    try:
        response = render_to_response('licenses-mobile.html', None)

        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response
    except:
        raise Http404

def mobileFaq(request):
    try:
        response = render_to_response('faq-mobile.html', None)

        response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
        response['Cache-Control'] = 'max-age=600'

        return response
    except:
        raise Http404

