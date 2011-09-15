#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import init

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response

def about(request):
    try:
        return render_to_response('about.html', None)
    except:
        raise Http404

def index(request):
    try:
        return render_to_response('index.html', None)
    except:
        raise Http404
    