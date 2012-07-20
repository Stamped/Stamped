#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import os, pprint, utils

from django.views.decorators.http   import require_http_methods
from django.http                    import HttpResponseRedirect

@require_http_methods(["GET", "POST"])
def error_404(request, **kwargs):
    # TODO
    return None

@require_http_methods(["GET", "POST"])
def error_503(request, **kwargs):
    # TODO
    return None

@require_http_methods(["GET", "POST"])
def error_500(request, **kwargs):
    # TODO
    return None

