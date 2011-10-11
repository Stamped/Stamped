#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, logs

from AStatsSink  import AStatsSink
from libs.StatsD import StatsD

class StatsDSink(AStatsSink):
    
    def __init__(self):
        self.statsd = StatsD(host='localhost', port=8125)
    
    def time(self, name, time, sample_rate=1):
        logs.debug("[%s] time: %s %0.3f ms" % (self, name, time))
        
        return self.statsd.time(name, time, sample_rate)
    
    def increment(self, name, sample_rate=1):
        logs.debug("[%s] increment: %s" % (self, name))
        
        return self.statsd.increment(name, sample_rate)
    
    def decrement(self, name, sample_rate=1):
        logs.debug("[%s] decrement: %s" % (self, name))
        
        return self.statsd.decrement(name, sample_rate)

