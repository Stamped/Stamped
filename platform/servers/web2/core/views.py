#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils

from django.http        import HttpResponseRedirect
from django.template    import RequestContext
from django.shortcuts   import render_to_response
from helpers            import *

@handleView
def index(request):
    autoplay_video = bool(request.GET.get('video', False))
    
    return render_to_response('index.html', locals(), context_instance=RequestContext(request))

@handleView
def blog(request):
    return HttpResponseRedirect('http://blog.stamped.com/')

@handleView
def profile(request, screen_name, **kwargs):
    user   = stampedAPIProxy.getUser(screen_name=screen_name)
    stamps = stampedAPIProxy.getUserStamps(user_id=user['user_id'])
    
    return render_to_response('demo.html', locals(), context_instance=RequestContext(request))

