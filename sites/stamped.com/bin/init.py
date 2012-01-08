#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__   = "TODO"

try:
    import gevent
except ImportError:
    raise Exception("required import gevent not found! have you activated the required virtualenv?")

import sys
# note: celeryd does not seem to work woth monkey patching enabled...
if not 'celery' in sys.modules and not 'celery.task' in sys.modules:
    # note: in order for gevent to work properly, this *must* be the first module 
    # imported from any other python file which needs stdlib to play well with 
    # gevent / greenlets (e.g., best practice is to always include this file first 
    # regardless of whether or not patching is required except in possible extreme 
    # cases).
    from gevent import monkey
    
    # patches stdlib (including socket and ssl modules) to cooperate with other greenlets
    monkey.patch_all()

# patch pymongo to be gevent async compatible 
# note: the pymongo patch appears to not play well with too many open connections
#import patch_pymongo

#-----------------------------------------------------------

import os, sys

base = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.join(base, "crawler"))
sys.path.insert(0, os.path.join(base, "api"))
sys.path.insert(0, base)

