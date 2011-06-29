#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, Utils

from abc import abstractmethod

class IASyncProducer():
    @abstractmethod
    def get(self, block = True, timeout=None):
        pass
    
    def get_nowait(self):
        return self.get(block=True, timeout=None)
    
    @abstractmethod
    def next(self):
        pass
    
    def __iter__(self):
        return self
    
    @abstractmethod
    def startProducing(self):
        pass

