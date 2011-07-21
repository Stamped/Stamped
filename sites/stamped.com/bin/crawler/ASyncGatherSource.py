#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils

from AEntityProxy import AEntityProxy

"""
from api.IASyncProducer import IASyncProducer

class ASyncGatherSource(IASyncProducer):
    
    def __init__(self, sources):
        self._sources = list(sources)
        self._started = False
    
    def startProducing(self):
        if not self._started:
            self._started = True
            source = self._source
            
            if source is not None:
                #utils.log("[ASyncGatherSource] start pulling from source %s" % str(source))
                source.startProducing()
    
    def get(self, block=True, timeout=None):
        source = self._source
        
        if source is not None:
            return source.get(block, timeout)
        else:
            raise queue.Empty
    
    def get_nowait(self):
        source = self._source
        
        if source is not None:
            return source.get_nowait()
        else:
            raise queue.Empty
    
    def next(self):
        source = self._source
        
        if source is not None:
            #utils.log("[ASyncGatherSource] next %s" % (str(source), ))
            item = source.next()
            
            if item is StopIteration:
                self._sources = self._sources[1:]
                
                source = self._source
                if source is not None:
                    #utils.log("[ASyncGatherSource] start pulling from source %s" % str(source))
                    source.startProducing()
                
                return self.next()
            else:
                return item
        else:
            return StopIteration
    
    @property
    def _source(self):
        if len(self._sources) > 0:
            return self._sources[0]
        else:
            return None
"""

class ASyncGatherSource(AEntityProxy):
    
    def __init__(self, sources, name=None):
        sources = list(sources)
        
        if name is None:
            name = "GatherSource(%d)" % (len(sources), )
        
        AEntityProxy.__init__(self, sources[0], name)
        self._sources = list(sources)
    
    def _run(self):
        for source in self._sources:
            source.startProducing()
            self.processQueue(source)
        
        self._output.put(StopIteration)
    
    def next(self):
        source = self.getSource()
        
        if source is not None:
            #utils.log("[ASyncGatherSource] next %s" % (str(source), ))
            item = source.next()
            
            if item is StopIteration:
                self._sources = self._sources[1:]
                
                source = self.getSource()
                if source is not None:
                    #utils.log("[ASyncGatherSource] start pulling from source %s" % str(source))
                    source.startProducing()
                
                return self.next()
            else:
                return item
        else:
            return StopIteration
    
    def getSource(self):
        if len(self._sources) > 0:
            return self._sources[0]
        else:
            return None

