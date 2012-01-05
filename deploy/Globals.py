#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__ = "TODO"

# note: in order for gevent to work properly, this *must* be the first module 
# imported from any other python file which needs stdlib to play well with 
# gevent / greenlets (e.g., best practice is to always include this file first 
# regardless of whether or not patching is required except in possible extreme 
# cases).
from gevent import monkey

# patches stdlib (including socket and ssl modules) to cooperate with other greenlets
monkey.patch_all()

#-----------------------------------------------------------

