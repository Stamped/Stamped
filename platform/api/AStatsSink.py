#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract

class AStatsSink(object):
    
    @abstract
    def time(self, name, time, samle_rate=1):
        pass
    
    @abstract
    def increment(self, name, samle_rate=1):
        pass
    
    @abstract
    def decrement(self, name, samle_rate=1):
        pass
    
    def __str__(self):
        return self.__class__.__name__

