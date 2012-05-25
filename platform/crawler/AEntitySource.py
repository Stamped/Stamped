#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, EntitySources, utils

from api.IASyncProducer import IASyncProducer
from gevent import Greenlet
from gevent.queue import Queue
from utils import abstract
import Entity

class AEntitySource(Greenlet, IASyncProducer):
    """
        Simple asynchronous entity producer
    """
    
    def __init__(self, name, types, maxQueueSize=None):
        Greenlet.__init__(self)
        
        self._name = name
        self._id = EntitySources.getSourceID(name)
        
        self._output = Queue(maxQueueSize)
        self._started = False
        self._maxQueueSize = maxQueueSize
        
        self.subcategories = types
        self.categories = set()
        
        # validate the types
        for t in types:
            if not t in Entity.subcategories:
                raise AttributeError("Source subcategory '%s' not supported" % t)
            
            self.categories.add(Entity.mapSubcategoryToCategory(t))
    
    def get(self, block=True, timeout=None):
        return self._output.get(block, timeout)
    
    def get_nowait(self):
        return self._output.get_nowait()
    
    def empty(self):
        return self._output.empty()
    
    def next(self):
        return self._output.next()
    
    def startProducing(self):
        if not self._started:
            self._started = True
            self.start()
    
    @abstract
    def _run(self):
        """Subclasses should override to process the pull-based loop in the 
        context of this sink's Greenlet."""
        pass
        #utils.log("")
        #utils.log("Importing entities from source '%s'" % self.name)
        #utils.log("")
    
    @property
    def name(self): return self._name
    
    @property
    def maxQueueSize(self): return self._maxQueueSize
    
    @abstract
    def getMaxNumEntities(self):
        raise NotImplementedError
    
    def __str__(self):
        return self.name

class AExternalEntitySource(AEntitySource):
    
    def __init__(self, name, types, maxQueueSize=None):
        AEntitySource.__init__(self, name, types, maxQueueSize)

class AExternalSiteEntitySource(AExternalEntitySource):
    """
        An external site which may be crawled as a source of entity data.
    """
    
    def __init__(self, name, types, maxQueueSize=None):
        AExternalEntitySource.__init__(self, name, types, maxQueueSize)
    
    def importAll(self, sink, limit=None):
        url = self.getNextURL()
        
        while url is not None and len(url) > 0 and ((not self.options.test) or len(self.entities) < 30):
            try:
                entities = self.getEntitiesFromURL(url)
                
                if not sink.addEntities(entities):
                    utils.log("Error storing %d entities to %s from %s" % \
                            (utils.count(entities), str(sink), url))
            except:
                utils.log("Error crawling " + url + "\n")
                utils.printException()
    
    @abstract
    def getNextURL(self):
        pass
    
    @abstract
    def getEntitiesFromURL(self, url, limit=None):
        pass

class AExternalServiceEntitySource(AExternalEntitySource):
    """
        An external service which may be queried as a source of entity data.
    """
    
    def __init__(self, name, types, maxQueueSize=None):
        AExternalEntitySource.__init__(self, name, types, maxQueueSize)
    
class AExternalDumpEntitySource(AExternalEntitySource):
    """
        An external data dump which may be crawled as a source of entity data 
        (e.g., compressed bulk datafile).
    """
    
    def __init__(self, name, types, maxQueueSize=None):
        AExternalEntitySource.__init__(self, name, types, maxQueueSize)

class AUserSource(AEntitySource):
    """
        User-entered / manual data source.
    """
    
    def __init__(self, name, types, maxQueueSize=None):
        AEntitySource.__init__(self, name, types, maxQueueSize)

