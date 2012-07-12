#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


import gevent
from gevent             import monkey
monkey.patch_all()

import rpyc
from GreenletServer     import GreenletServer
from RateLimiter        import RateLimiter, Request

from optparse           import OptionParser

limiters = {
    'facebook'      : RateLimiter(                      fail_limit=10,      fail_dur=60),
    'twitter'       : RateLimiter(                      fail_limit=10,      fail_dur=60),
    'netflix'       : RateLimiter(cps=4,    cpd=100000, ),#fail_limit=10,      fail_dur=60),
    'rdio'          : RateLimiter(          cpd=15000,  fail_limit=10,      fail_dur=60),
    'spotify'       : RateLimiter(                      fail_limit=10,      fail_dur=60),
    }


count = 0

class StampedRateLimiterService(rpyc.Service):

    def on_connect(self):
        # code that runs when a connection is created
        # (to init the serivce, if needed
        pass

    def on_disconnect(self):
        # code that runs when the connection has already closed
        # (to finalize the service, if needed)
        pass

    def exposed_request(self, service, priority, timeout, verb, url, body = {}, headers = {}):
        global count
        count += 1
        if timeout is None:
            raise StampedInputError("Timeout period must be provided")
        request = Request(timeout, verb, url, body, headers)
        request.number = count

        limiter = limiters[service]

        asyncresult = limiter.addRequest(request, priority)

        # This sleep call is necessary because of a bug with the way gevent handles timeouts... Effectively resets
        # the starting time for the timeout, otherwise the starting time is the time of last pop from queue
        #gevent.sleep(0)
        return asyncresult.get(block=True, timeout=timeout)


def runServer(port=18861):
    t = GreenletServer(StampedRateLimiterService, port = port)
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
    import sys
    options     = parseCommandLine()
    options     = options.__dict__
    port        = options.pop('port', 18861)

    runServer(port)
