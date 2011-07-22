#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils

from IASyncConsumer import IASyncConsumer
from gevent.queue import Queue
from gevent import Greenlet
from abc import abstractmethod

class AEntitySink(Greenlet, IASyncConsumer):
    """
        Abstract entity sink which is capable of consuming entities via both 
        push and pull-based mechanisms.
    """
    
    def __init__(self, desc, maxQueueSize=None):
        Greenlet.__init__(self)
        self._desc  = desc
        self._input = Queue(maxQueueSize)
    
    def put(self, item, block=True, timeout=None):
        """Inserts an item into this sink's queue"""
        self._input.put(item, block, timeout)
    
    def put_nowait(self, item):
        """Inserts an item into this sink's queue only if it would be non-blocking"""
        self._input.put_nowait(item)
    
    @abstractmethod
    def _run(self):
        """Subclasses should override to process the pull-based loop in the 
        context of this sink's Greenlet."""
        pass
    
    def processQueue(self, queue):
        """Processes the given queue as many items at a time as possible between 
        blocking until StopIteration is received."""
        #utils.log("[%s] AEntitySink.processQueue" % (self, ))
        stop = False
        
        while not stop:
            items = []
            
            item = queue.get()
            if item is StopIteration:
                stop = True
                break
            
            if item is not None:
                items.append(item)
            
            # retrieve as many items in the input queue at once to process  
            # multiple items at a time if possible
            while not queue.empty():
                item = queue.get_nowait()
                
                if item is StopIteration:
                    stop = True
                    break
                
                if item is not None:
                    items.append(item)
            
            if len(items) > 1:
                self._processItems(items)
            else:
                self._processItem(items[0])
    
    @abstractmethod
    def _processItem(self, item):
        """Consumes one item."""
        pass
    
    @abstractmethod
    def _processItems(self, items):
        """Consumes all of the items."""
        pass
    
    def __str__(self):
        return self._desc

