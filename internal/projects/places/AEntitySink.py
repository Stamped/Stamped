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
    
    def processQueue(self, queue):
        #Utils.log("[%s] AEntitySink.processQueue" % (self, ))
        stop = False
        
        while not stop:
            items = []
            
            item = queue.get()
            if item is StopIteration:
                stop = True
                break
            
            items.append(item)
            
            # retrieve as many items in the input queue at once to process  
            # multiple items at a time if possible
            while not queue.empty():
                item = queue.get_nowait()
                
                if item is StopIteration:
                    stop = True
                    break
                
                items.append(item)
            
            if len(items) > 1:
                self._processItems(items)
            else:
                self._processItem(items[0])
    
    @abstractmethod
    def _processItem(self, item):
        pass
    
    @abstractmethod
    def _processItems(self, items):
        pass
    
    def __str__(self):
        return self._desc

