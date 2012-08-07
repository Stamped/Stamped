#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from gevent.pool import Pool
from gevent import Greenlet
from api_old.AEntitySink import AEntitySink
from crawler.AEntitySource import AEntitySource
from api_old.IASyncProducer import IASyncProducer

class AEntityProxy(AEntitySink, AEntitySource):
    
    def __init__(self, source):
        if source is None:
            name = "%s(None)" % (self.__class__.__name__)
            maxQueueSize = 1
            types = []
        else:
            name = "%s(%s)" % (self.__class__.__name__, source.name)
            maxQueueSize = source.maxQueueSize
            types = source.subcategories
        
        AEntitySink.__init__(self, name, maxQueueSize)
        AEntitySource.__init__(self, name, types, maxQueueSize)
        
        self._source = source
        self._started = False
        self._pool = Pool(maxQueueSize)
    
    def _run(self):
        utils.log("[%s] pulling from source '%s'" % (self.name, self._source.name))
        
        self._source.startProducing()
        self.processQueue(self._source._output)
        self._source.join()
        self._output.put(StopIteration)
    
    def join(self):
        self._source.join()
        self._pool.join()
        Greenlet.join(self)
    
    def _processItem(self, item):
        #utils.log("[%s] _processItem %s" % (self.name, str(type(item)), ))
        
        if item is not StopIteration:
            item = self._transform(item)
        
        if isinstance(item, (tuple, list, )):
            for i in item:
                if i is not None:
                    self._output.put(i)
        else:
            if item is not None:
                self._output.put(item)
    
    def _processItems(self, items):
        for item in items:
            self._pool.spawn(self._processItem, item)
        
        # TODO: understand *exactly* why this is necessary here!
        #self._pool.join()
    
    def _transform(self, entity):
        return entity

