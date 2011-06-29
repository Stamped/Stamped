#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, Utils

from IASyncProducer import IASyncProducer

class ASyncGatherSource(IASyncProducer):
    
    def __init__(self, sources):
        self._sources = list(sources)
        self._started = False
    
    def startProducing(self):
        if not self._started:
            self._started = True
            source = self._source
            
            if source is not None:
                #Utils.log("[ASyncGatherSource] start pulling from source %s" % str(source))
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
            item = source.next()
            
            if isinstance(item, StopIteration):
                self._sources = self._sources[1:]
                
                source = self._source
                if source is not None:
                    #Utils.log("[ASyncGatherSource] start pulling from source %s" % str(source))
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

