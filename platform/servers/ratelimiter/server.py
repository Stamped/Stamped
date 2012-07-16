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
config_load_interval = 10*1
count = 0


def configLoaderLoop(service):
    while True:
        sleep(config_load_interval)
        try:
            service.loadLimiters()
        except:
            pass

class StampedRateLimiterService():

    def __init__(self, throttle=False):
        print('calling ratelimiterService init')
        self.__throttle = throttle
        self.__limiters = {}
        self.loadLimiters()
        self.__config_loader = gevent.spawn(configLoaderLoop, self)

    def loadLimiters(self):
        print('checking config file for updates')
        try:
            meta = {}
            if os.path.exists(limits_path):
                with open(limits_path, "rb") as fp:
                    source = fp.read()

                exec compile(source, limits_path, "exec") in meta
            else:
                print("### Could not find limits.conf: no limits defined")
                return
        except Exception as e:
            print('Exception while trying to execute limits.conf file: %s' % e)
            return

        try:
            limits = meta['limits']
        except:
            print('limits var is not being set in limits.conf.  skipping load step')
            return

        for l in limits:
            service_name = None
            try:
                service_name = l['service_name']
                limit = l.get('limit', None)
                period = l.get('period', None)
                cpd = l.get('cpd', None)
                fail_limit = l.get('fail_limit', None)
                fail_period = l.get('fail_period', None)
                fail_wait = l.get('fail_wait', None)
                if self.__throttle:
                    limit = max(1, limit / 10)
                    cpd = max(1, cpd / 10)
            except Exception as e:
                if service_name is not None:
                    print ("Exception while reading limiter for service '%s' in limits.conf, skipping" % service_name)
                else:
                    print ('Exception while reading limiter in limits.conf, skipping')
                continue

            try:
                limiter = self.__limiters.get(service_name, None)
                if limiter is not None:
                    limiter.update_limits(limit, period, cpd, fail_limit, fail_period, fail_wait)
                else:
                    print("adding rate limiter for service '%s'" % service_name)
                    self.__limiters[service_name] = RateLimiter(service_name, limit, period, cpd, fail_limit, fail_period, fail_wait)
            except:
                print ("Exception thrown while attempting to update or create RateLimiter '%s'. Skipping" % service_name)
                return

    def handleRequest(self, service, priority, timeout, verb, url, body = {}, headers = {}):
        global count
        count += 1
        print ('calling exposed_request')
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

__rlServiceGlobal = None
def globalRateLimiterService():
    global __rlServiceGlobal
    if __rlServiceGlobal is None:
        __rlServiceGlobal = StampedRateLimiterService()
    return __rlServiceGlobal

class StampedRateLimiterRPCService(rpyc.Service):

    def __init__(self, port):
        print('calling ratelimiterRPCService init')
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

    def exposed_request(self, service, priority, timeout, verb, url, body = {}, headers = {}):
        return self.__rl_service.handleRequest(service, priority, timeout, verb, url, body, headers)


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
    import sys
    options     = parseCommandLine()
    options     = options.__dict__
    port        = options.pop('port', 18861)

    runServer(port)
