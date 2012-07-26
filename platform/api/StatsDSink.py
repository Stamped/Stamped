#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils, logs
import libs.ec2_utils, pickle, os, time

from api.AStatsSink     import AStatsSink
from libs.StatsD    import StatsD
from gevent.pool    import Pool
from pprint         import pformat

class StatsDSink(AStatsSink):
    
    def __init__(self, stampedAPI):
        self.statsd = StatsD(host="localhost", port=8125)
        self.stampedAPI = stampedAPI
        
        self._pool = Pool(1)
        if not self.stampedAPI.lite_mode:
            self._pool.spawn(self._init)
    
    def _init(self):
        # NOTE: disabling StatsD for V2 launch
        return
        
        time.sleep(15)
        logs.info("initializing StatsD")
        host, port = "localhost", 8125
        
        if utils.is_ec2():
            done = False
            sleep = 1
            
            while not done:
                try:
                    stack_info = libs.ec2_utils.get_stack()
                    
                    if stack_info is None:
                        raise
                    
                    for node in stack_info.nodes:
                        if 'monitor' in node.roles:
                            host, port = node.private_ip_address, 8125
                            done = True
                            break
                except:
                    utils.printException()
                    sleep *= 2
                    time.sleep(sleep)
                    
                    if sleep > 32:
                        logs.warning("ERROR initializing StatsD!!!")
                        return
        else:
            return
        
        logs.info("initializing StatsD at %s:%d" % (host, port))
        self.statsd = StatsD(host, port)
    
    def time(self, name, time, sample_rate=1):
        logs.debug("[%s-%s:%d] time: %s %0.3f ms" % (self, self.statsd.addr[0], self.statsd.addr[1], name, time))
        
        return self.statsd.time(name, time, sample_rate)
    
    def increment(self, name, sample_rate=1):
        logs.debug("[%s-%s:%d] increment: %s" % (self, self.statsd.addr[0], self.statsd.addr[1], name))
        
        if 0 == sample_rate:
            return
        
        return self.statsd.increment(name, sample_rate)
    
    def decrement(self, name, sample_rate=1):
        logs.debug("[%s-%s:%d] decrement: %s" % (self, self.statsd.addr[0], self.statsd.addr[1], name))
        
        if 0 == sample_rate:
            return
        
        return self.statsd.decrement(name, sample_rate)

