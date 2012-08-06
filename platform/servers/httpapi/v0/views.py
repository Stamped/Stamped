#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import os

from django.http import HttpResponse

ROOT = os.path.dirname(os.path.abspath(__file__))

def _getDoc(name):
    try:
        f = open(os.path.join(ROOT, 'docs/%s.html' % name))
        ret = f.read()
        f.close()
        return HttpResponse(ret)
    except Exception as e:
        response = HttpResponse("error")
        response.status_code = 500
        return response

def index(request):
    return _getDoc('Index')

def oauth2(request):
    return _getDoc('OAuth2')

def account(request):
    return _getDoc('Account')

def users(request):
    return _getDoc('Users')

def friendships(request):
    return _getDoc('Friendships')

def entities(request):
    return _getDoc('Entities')

def stamps(request):
    return _getDoc('Stamps')

def comments(request):
    return _getDoc('Comments')

def collections(request):
    return _getDoc('Collections')

def favorites(request):
    return _getDoc('Favorites')

def activity(request):
    return _getDoc('Activity')

def temp(request):
    return _getDoc('Temp')

def default(request):
    return HttpResponse("This is where the API will go.")

