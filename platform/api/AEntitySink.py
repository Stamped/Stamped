#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from utils import abstract

from api.IASyncConsumer import IASyncConsumer
from gevent.queue import Queue, Empty
from gevent import Greenlet
from gevent.pool import Pool

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
    
    def _run(self):
        """Subclasses should override to process the pull-based loop in the 
        context of this sink's Greenlet."""
        pass
    
    def processQueue(self, queue, async=True, poolSize=128):
        """Processes the given queue as many items at a time as possible between 
        blocking until StopIteration is received."""
        #utils.log("[%s] >>> AEntitySink.processQueue" % (self, ))
        stop = 0
        if async:
            pool = utils.LoggingThreadPool(poolSize)
        
        while True:
            items = []
            
            if stop == 0:
                try:
                    item = queue.get(timeout=3600)
                except Empty:
                    utils.log("[%s] ERROR: timeout in queue.get (%s)" % (self, queue))
                    break
                
                if item is StopIteration:
                    stop = 1
                elif item is not None:
                    items.append(item)
            
            # retrieve as many items in the input queue at once to process 
            # multiple items at a time if possible
            while not queue.empty():
                item = queue.get_nowait()
                
                if item is StopIteration:
                    stop = 1
                    break
                
                if item is not None:
                    items.append(item)
            
            #utils.log("[%s] %d" % (self, len(items)))
            
            numItems = len(items)
            if numItems > 1:
                if async:
                    pool.spawn(self._processItems, items)
                else:
                    self._processItems(items)
            elif numItems == 1:
                if async:
                    pool.spawn(self._processItem, items[0])
                else:
                    self._processItem(items[0])
            
            if stop == 2:
                break
            
            if stop == 1:
                if hasattr(queue, 'join'):
                    queue.join()
                stop = 2
        
        if async:
            pool.join()
        #utils.log("[%s] <<< AEntitySink.processQueue" % (self, ))
    
    @abstract
    def _processItem(self, item):
        """Consumes one item."""
        pass
    
    @abstract
    def _processItems(self, items):
        """Consumes all of the items."""
        pass
    
    def __str__(self):
        return self._desc

