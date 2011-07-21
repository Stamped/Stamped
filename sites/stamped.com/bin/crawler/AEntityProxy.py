#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, Utils

from gevent.pool import Pool
from AEntitySink import AEntitySink
from AEntitySource import AEntitySource
from IASyncProducer import IASyncProducer

class AEntityProxy(AEntitySink, AEntitySource):
    
    def __init__(self, source, name):
        name = "%s Proxy(%s)" % (name, source.name)
        AEntitySink.__init__(self, name, source.maxQueueSize)
        AEntitySource.__init__(self, name, source.types, source.maxQueueSize)
        
        self._source = source
        self._started = False
        self._pool = Pool(source.maxQueueSize)
    
    def _run(self):
        Utils.log("[%s] pulling from source '%s'" % (self.name, self._source.name))
        
        self._source.startProducing()
        self.processQueue(self._source._output)
        self._output.put(StopIteration)
    
    """ TODO: verify that overriding join is necessary
    def join(self):
        self._source.join()
        self._pool.join()
        Greenlet.join(self)
    """
    
    def _processItem(self, item):
        #Utils.log("[%s] _processItem %s" % (self.name, str(item), ))
        
        if item is not StopIteration:
            item = self._transform(item)
        
        self._output.put(item)
    
    def _processItems(self, items):
        for item in items:
            self._pool.spawn(self._processItem, item)
        
        # self._pool.join()
    
    def _transform(self, entity):
        return entity

