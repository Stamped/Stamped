#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from utils import abstract

class IASyncProducer():
    """
        Interface for an asynchronous, pull-based producer.
    """
    
    @abstract
    def get(self, block = True, timeout=None):
        pass
    
    def get_nowait(self):
        return self.get(block=False, timeout=None)
    
    @abstract
    def empty(self):
        pass
    
    @abstract
    def next(self):
        pass
    
    def __iter__(self):
        return self
    
    @abstract
    def startProducing(self):
        pass

