#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils

from django.views.decorators.http   import require_http_methods
from django.http                    import HttpResponseRedirect

from servers.web2.core.schemas      import *
from servers.web2.core.helpers      import *

@stamped_view()
def error_404(request, **kwargs):
    body_classes = "error 404"
    
    return stamped_render(request, '404.html', {
        'body_classes'      : body_classes, 
        'page'              : '404', 
        'title'             : 'Stamped - 404 Error Not Found', 
    })

@stamped_view()
def error_500(request, **kwargs):
    body_classes = "error 500"
    
    return stamped_render(request, '500.html', {
        'body_classes'      : body_classes, 
        'page'              : '500', 
        'title'             : 'Stamped - 500 Internal Server Error', 
    })

