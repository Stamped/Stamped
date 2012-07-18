#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


import gevent
from gevent             import monkey
monkey.patch_all()

import os
import rpyc
from time               import sleep
from GreenletServer     import GreenletServer
import RateLimiter2
from RateLimiter2       import RateLimiter, Request

from optparse           import OptionParser


limits_path = os.path.dirname(RateLimiter2.__file__) + '/limits.conf'
config_load_interval = 60*5
count = 0


def configLoaderLoop(service):
    while True:
        sleep(config_load_interval)
        service.loadLimiters()


class StampedRateLimiterService(rpyc.Service):

    def __init__(self, port, throttle=False):
        rpyc.Service.__init__(self, port)
        self.__throttle = throttle
        self.__limiters = {}
        self.loadLimiters()
        self.__config_loader = gevent.spawn(configLoaderLoop, self)

    def loadLimiters(self):
        meta = {}
        if os.path.exists(limits_path):
            with open(limits_path, "rb") as fp:
                source = fp.read()

            exec compile(source, limits_path, "exec") in meta
        else:
            print("### Could not find limits.conf: no limits defined")
            return

        limits = meta['limits']
        limiters = {}
        if self.__throttle:
            for l in limits:
                limit   = max(1, l['limit'] / 10)
                cpd     = max(1, l['cpd'] / 10)
                limiter = RateLimiter(limit, l['period'], cpd, l['fail_limit'], l['fail_period'], l['fail_wait'])
                limiters[l['service_name']] = limiter
        else:
            for l in limits:
                limiter = RateLimiter(l['limit'], l['period'], l['cpd'], l['fail_limit'], l['fail_period'], l['fail_wait'])
                limiters[l['service_name']] = limiter

        if self.__limiters is None:
            self.__limiters = limiters
            return

        for k,v in limiters.iteritems():
            if self.__limiters.get(k, None) is not None:
                self.__limiters[k].update_limits(v.limit, v.period, v.cpd, v.fail_limit, v.fail_period, v.fail_wait)
            else:
                self.__limiters[k] = v

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

        limiter = self.__limiters[service]

        priority_int = 0
        if priority != 'high':
            priority_int = 10

        asyncresult = limiter.addRequest(request, priority_int)

        # This sleep call is necessary because of a bug with the way gevent handles timeouts... Effectively resets
        # the starting time for the timeout, otherwise the starting time is the time of last pop from queue
        gevent.sleep(0)
        response = asyncresult.get(block=True, timeout=timeout)
        #print('### returning from exposed_request')
        return response


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
