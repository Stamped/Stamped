#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import datetime

from django.http        import HttpResponse, Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts   import render_to_response

### WEBSITE

def VIEW(f):
    def _wrapper(*args, **kwargs):
        try:
            response = f(*args, **kwargs)
            
            response['Expires'] = (datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).ctime()
            response['Cache-Control'] = 'max-age=600'
            
            return response
        except:
            raise Http404
    return _wrapper

@VIEW
def index(request):
    autoplay_video = bool(request.GET.get('video', False))
    
    return render_to_response('index.html', locals())

@VIEW
def blog(request):
    return HttpResponseRedirect('http://blog.stamped.com/')

