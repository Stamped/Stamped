#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils

import servers.web2.core.views as views

def profile(*args, **kwargs):
    kwargs['mobile'] = True
    
    return views.profile(*args, **kwargs)

def map(*args, **kwargs):
    kwargs['mobile'] = True
    
    return views.map(*args, **kwargs)

