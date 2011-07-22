#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils

from abc import abstractmethod

class IASyncConsumer():
    """
        Interface for an asynchronous, push-based consumer.
    """
    
    @abstractmethod
    def put(self, item, block=True, timeout=None):
        pass
    
    def put_nowait(self, item):
        self.put(item, block=False, timeout=None)
    
    def close(self):
        pass

