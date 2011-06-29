#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, Utils

from abc import abstractmethod

class IASyncConsumer():
    @abstractmethod
    def put(self, item, block=True, timeout=None):
        pass
    
    def put_nowait(self, item):
        self.put(item, block=False, timeout=None)
    
    def close():
        pass

