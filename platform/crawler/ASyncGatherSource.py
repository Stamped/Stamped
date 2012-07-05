#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from crawler.AEntityProxy import AEntityProxy

class ASyncGatherSource(AEntityProxy):
    
    def __init__(self, sources):
        sources = list(sources)
        
        AEntityProxy.__init__(self, sources[0])
        self._sources = list(sources)
    
    def _run(self):
        for source in self._sources:
            source.startProducing()
            self.processQueue(source)
            source.join()
        
        self._output.put(StopIteration)
    
    def next(self):
        source = self.getSource()
        
        if source is not None:
            #utils.log("[ASyncGatherSource] next %s" % (str(source), ))
            while True:
                item = source.next()
                
                if item is StopIteration:
                    self._sources = self._sources[1:]
                    
                    source = self.getSource()
                    if source is not None:
                        #utils.log("[ASyncGatherSource] start pulling from source %s" % str(source))
                        source.startProducing()
                    
                    return self.next()
                elif item is not None:
                    return item
        else:
            return StopIteration
    
    def getSource(self):
        if len(self._sources) > 0:
            return self._sources[0]
        else:
            return None

