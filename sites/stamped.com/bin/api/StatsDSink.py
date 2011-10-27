#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, utils, logs
import time

from AStatsSink     import AStatsSink
from libs.EC2Utils  import EC2Utils
from libs.StatsD    import StatsD
from gevent.pool    import Pool
from pprint         import pformat

class StatsDSink(AStatsSink):
    
    def __init__(self):
        self.statsd = StatsD(host="localhost", port=8125)
        self._pool  = Pool(1)
        self._pool.spawn(self._init)
        time.sleep(0.01)
    
    def _init(self):
        logs.info("initializing StatsD")
        host, port = "localhost", 8125
        
        if True: #utils.is_ec2():
            ec2_utils = EC2Utils()
            done = False
            
            while not done:
                try:
                    utils.log("EC2UTILS GET_STACK_INFO 1")
                    
                    stack_info = ec2_utils.get_stack_info(stack='dk2')
                    
                    utils.log("EC2UTILS GET_STACK_INFO 2")
                    utils.log(pformat(dict(stack_info)))
                    
                    for node in stack_info.nodes:
                        if 'monitor' in node.roles:
                            host, port = node.private_dns, 8125
                            done = True
                            break
                except:
                    utils.printException()
                    pass
        
        logs.info("initializing StatsD at %s:%d" % (host, port))
        self.statsd = StatsD(host, port)
    
    def time(self, name, time, sample_rate=1):
        logs.debug("[%s] time: %s %0.3f ms" % (self, name, time))
        
        return self.statsd.time(name, time, sample_rate)
    
    def increment(self, name, sample_rate=1):
        logs.debug("[%s] increment: %s" % (self, name))
        
        return self.statsd.increment(name, sample_rate)
    
    def decrement(self, name, sample_rate=1):
        logs.debug("[%s] decrement: %s" % (self, name))
        
        return self.statsd.decrement(name, sample_rate)

