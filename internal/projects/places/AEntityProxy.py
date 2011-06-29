#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, Utils

from IASyncProducer import IASyncProducer

class AEntityProxy(IASyncProducer):
    
    def __init__(self, source, desc):
        self._source = source
        self._desc = desc
        self._started = False
    
    def startProducing(self):
        if not self._started:
            self._started = True
            self._source.startProducing()
    
    def get(self, block=True, timeout=None):
        return self._transform(self._source.get(block, timeout))
    
    def get_nowait(self):
        return self._transform(self._source.get_nowait())
    
    def next(self):
        item = self._source.next()
        
        if isinstance(item, StopIteration):
            return item
        else:
            return self._transform(item)
    
    def _transform(self, entity):
        return entity
    
    def __str__(self):
        return self._desc

