#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, Utils

from IASyncConsumer import IASyncConsumer
from gevent.queue import Queue
from gevent import Greenlet
from abc import abstractmethod

class AEntitySink(Greenlet, IASyncConsumer):
    
    def __init__(self, desc, maxQueueSize=None):
        Greenlet.__init__(self)
        self._desc  = desc
        self._input = Queue(maxQueueSize)
    
    def put(self, item, block=True, timeout=None):
        self._input.put(item, block, timeout)
    
    def put_nowait(self, item):
        self._input.put_nowait(item)
    
    @abstractmethod
    def _run(self):
        pass
    
    def __str__(self):
        return self._desc

