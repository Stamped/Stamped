#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, EntitySources, Utils

from IASyncProducer import IASyncProducer
from gevent import Greenlet
from gevent.queue import Queue
from abc import abstractmethod

class AEntitySource(Greenlet, IASyncProducer):
    """
        Simple asynchronous entity producer
    """
    
    _supportedTypes = set([ 'place', 'contact', 'restaurant', 'iPhoneApp', 'book', 'movie' ])
    
    def __init__(self, name, types=None, maxQueueSize=None):
        Greenlet.__init__(self)
        
        self._name = name
        self._id = EntitySources.getSourceID(name)
        if types is None:
            types = set()
        
        self._types = types
        self._output = Queue(maxQueueSize)
        self._started = False
        self.limit = None
        
        # validate the types
        for t in types:
            if not t in self._supportedTypes:
                raise AttributeError("Source category '%s' not supported" % t)
    
    def get(self, block=True, timeout=None):
        return self._output.get(block, timeout)
    
    def get_nowait(self):
        return self._output.get_nowait()
    
    def next(self):
        return self._output.next()
    
    def startProducing(self):
        if not self._started:
            self._started = True
            self.start()
    
    @abstractmethod
    def _run(self):
        pass
        #Utils.log("")
        #Utils.log("Importing entities from source '%s'" % self.name)
        #Utils.log("")
    
    @property
    def name(self): return self._name
    
    @property
    def types(self): return self._types

class AExternalEntitySource(AEntitySource):
    
    def __init__(self, name, types=None, maxQueueSize=None):
        AEntitySource.__init__(self, name, types, maxQueueSize)

class AExternalSiteEntitySource(AExternalEntitySource):
    """
        An external site which may be crawled as a source of entity data.
    """
    
    def __init__(self, name, types=None, maxQueueSize=None):
        AExternalEntitySource.__init__(self, name, types, maxQueueSize)
    
    def importAll(self, sink, limit=None):
        url = self.getNextURL()
        
        while url is not None and len(url) > 0 and ((not self.options.test) or len(self.entities) < 30):
            try:
                entities = self.getEntitiesFromURL(url)
                
                if not sink.addEntities(entities):
                    Utils.log("Error storing %d entities to %s from %s" % \
                            (Utils.count(entities), str(sink), url))
            except:
                Utils.log("Error crawling " + url + "\n")
                Utils.printException()
    
    @abstractmethod
    def getNextURL(self):
        pass
    
    @abstractmethod
    def getEntitiesFromURL(self, url, limit=None):
        pass

class AExternalServiceEntitySource(AExternalEntitySource):
    """
        An external service which may be queried as a source of entity data.
    """
    
    def __init__(self, name, types=None, maxQueueSize=None):
        AExternalEntitySource.__init__(self, name, types, maxQueueSize)
    
    def importAll(self, sink, limit=None):
        return True

class AExternalDumpEntitySource(AExternalEntitySource):
    """
        An external data dump which may be crawled as a source of entity data 
        (e.g., compressed bulk datafile).
    """
    
    def __init__(self, name, types=None, maxQueueSize=None):
        AExternalEntitySource.__init__(self, name, types, maxQueueSize)

class AUserSource(AEntitySource):
    """
        User-entered / manual data source.
    """
    
    def __init__(self, name, types=None, maxQueueSize=None):
        AEntitySource.__init__(self, name, types, maxQueueSize)

