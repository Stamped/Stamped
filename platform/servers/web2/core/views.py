#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import os, utils

from django.http    import HttpResponse, HttpResponseRedirect
from helpers        import *

@stamped_view
def index(request):
    autoplay_video = bool(request.GET.get('video', False))
    
    return stamped_render(request, 'index.html', locals())

@stamped_view
def blog(request):
    return HttpResponseRedirect('http://blog.stamped.com/')

@stamped_view
def profile(request, screen_name, **kwargs):
    user   = stampedAPIProxy.getUser(screen_name=screen_name)
    stamps = stampedAPIProxy.getUserStamps(user_id=user['user_id'])
    
    return stamped_render(request, 'demo.html', locals())

@stamped_view
def test(request, **kwargs):
    screen_name = 'travis'
    
    path = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(os.path.join(os.path.join(path, '..'), 'html'), 'test.html')
    
    with open(path, 'r') as f:
        source = f.read()
    
    return HttpResponse(source, content_type='text/html')

