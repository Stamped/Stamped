#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils

from abc import abstractmethod

class IASyncProducer():
    """
        Interface for an asynchronous, pull-based producer.
    """
    
    @abstractmethod
    def get(self, block = True, timeout=None):
        pass
    
    def get_nowait(self):
        return self.get(block=False, timeout=None)
    
    @abstractmethod
    def empty(self):
        pass
    
    @abstractmethod
    def next(self):
        pass
    
    def __iter__(self):
        return self
    
    @abstractmethod
    def startProducing(self):
        pass

