#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from gevent             import monkey
monkey.patch_all()

import Globals
import pickle
import rpyc
from GreenletServer     import GreenletServer
from servers.ratelimiter.RateLimiterService import StampedRateLimiterService
#from servers.ratelimiter.RateLimiter2 import TooManyFailedRequestsException, WaitTooLongException, DailyLimitException, TimeoutException

from optparse           import OptionParser

__rlServiceGlobal = None
def globalRateLimiterService():
    global __rlServiceGlobal
    if __rlServiceGlobal is None:
        print('creating ratelimiter service')
        __rlServiceGlobal = StampedRateLimiterService()
    return __rlServiceGlobal

class StampedRateLimiterRPCService(rpyc.Service):

    def __init__(self, port):
        rpyc.Service.__init__(self, port)
        self.__rl_service = globalRateLimiterService()


    def on_connect(self):
        # code that runs when a connection is created
        # (to init the serivce, if needed
        pass

    def on_disconnect(self):
        # code that runs when the connection has already closed
        # (to finalize the service, if needed)
        pass

    def exposed_request(self, service, priority, timeout, verb, url, body = None, headers = None):
        logs.info('Received request.  service: %s  priority: %s  timeout: %s  verb: %s  url: %s  body: %s  headers: %s' %
                  (service, priority, timeout, verb, url, body, headers))
        if body is not None:
            body = pickle.loads(body)
        if headers is not None:
            headers = pickle.loads(headers)
        response, content = self.__rl_service.handleRequest(service, priority, timeout, verb, url, body, headers)
        return pickle.dumps(response), content

def runServer(port=18861):
    t = GreenletServer(StampedRateLimiterRPCService, port =port)
    t.start()

def parseCommandLine():
    usage   = "Usage: %prog [options] command [args]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)

    parser.add_option("-p", "--port", dest="port",
        default=18861, type="int", help="Set server port")

    (options, args) = parser.parse_args()

    return options

if __name__ == "__main__":
    options     = parseCommandLine()
    options     = options.__dict__
    port        = options.pop('port', 18861)

    runServer(port)
