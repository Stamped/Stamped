#!/usr/bin/env python

"""
    Top-level module imported by all of the Stamped platform which accomplishes 
    two main things, the first and most important of which is to enable 
    otherwise isolated python modules to reference each other, and the second 
    is to "monkey-patch" stdlib for use with gevent's cooperative multitasking.
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

try:
    import gevent
except ImportError:
    raise Exception("required import gevent not found! have you activated the required virtualenv?")

import os, sys

# note: in order for gevent to work properly, this *must* be the first module 
# imported from any other python file which needs stdlib to play well with 
# gevent / greenlets (e.g., best practice is to always include this file first 
# regardless of whether or not patching is required except in possible extreme 
# cases).
from gevent import monkey

# patches stdlib (including socket and ssl modules) to cooperate with other greenlets
monkey.patch_all()

#-----------------------------------------------------------

base = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, os.path.join(base, "crawler"))
sys.path.insert(0, os.path.join(base, "api"))
sys.path.insert(0, base)

