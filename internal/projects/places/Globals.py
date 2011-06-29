#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from gevent import monkey

# patches stdlib (including socket and ssl modules) to cooperate with other greenlets
monkey.patch_all()

import Utils
#from ThreadPool import ThreadPool

#-----------------------------------------------------------

#__MAX_CONCURRENCY = 256

#threadPool = ThreadPool(__MAX_NUM_THREADS)

