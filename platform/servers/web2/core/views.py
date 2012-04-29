#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils

from django.http    import HttpResponseRedirect
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

