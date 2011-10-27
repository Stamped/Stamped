#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, utils, logs
import json, os, time

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
        
        if utils.is_ec2():
            ec2_utils = EC2Utils()
            done = False
            
            path = os.path.join(os.path.abspath(os.path.dirname(__file__)), '.stack.txt')
            
            while not done:
                try:
                    utils.log("EC2UTILS GET_STACK_INFO 1")
                    
                    stack_info = None
                    if os.path.exists(path):
                        try:
                            f = open(path, 'r')
                            stack_info = json.load(f)
                        except:
                            stack_info = None
                        finally:
                            f.close()
                    
                    if stack_info is None:
                        stack_info = ec2_utils.get_stack_info()
                        
                        try:
                            f = open(path, 'w')
                            json.dump(stack_info, f)
                        except:
                            pass
                        finally:
                            f.close()
                    
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
        logs.debug("[%s-%s:%d] time: %s %0.3f ms" % (self, self.statsd.addr[0], self.statsd.addr[1], name, time))
        
        return self.statsd.time(name, time, sample_rate)
    
    def increment(self, name, sample_rate=1):
        logs.debug("[%s-%s:%d] increment: %s" % (self, self.statsd.addr[0], self.statsd.addr[1], name))
        
        return self.statsd.increment(name, sample_rate)
    
    def decrement(self, name, sample_rate=1):
        logs.debug("[%s-%s:%d] decrement: %s" % (self, self.statsd.addr[0], self.statsd.addr[1], name))
        
        return self.statsd.decrement(name, sample_rate)

