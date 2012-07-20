#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


import gevent
from gevent             import monkey
monkey.patch_all()
from gevent.hub         import GreenletExit

import os
from time               import sleep
from datetime           import datetime
import RateLimiter2
from RateLimiter2       import RateLimiter, Request
from libs.ec2_utils     import get_stack

from db.mongodb.MongoRateLimiterLogCollection import MongoRateLimiterLogCollection


LIMITS_DIR = os.path.dirname(RateLimiter2.__file__)
CONFIG_LOAD_INTERVAL = 60*3
UPDATE_LOG_INTERVAL  = 60*3 # seconds to wait between updating the db with log of daily calls to each service


def configLoaderLoop(service, interval):
    while True:
        sleep(interval)
        try:
            service.loadLimiterConfig()
        except:
            pass

def updateLogLoop(service, interval):
    while True:
        sleep(interval)
        try:
            service.updateDbLog()
        except:
            pass



class StampedRateLimiterService():

    def __init__(self, throttle=False):
        print('calling ratelimiterService init')
        self.__throttle = throttle
        self.__limiters = {}
        self.__stack_name = get_stack().instance.stack if get_stack() is not None else 'local'
        self.__rllog = MongoRateLimiterLogCollection()
        self.loadDbLog()
        self.loadLimiterConfig()
        self.__config_loader_thread = None
        self.__update_log_thread = None
        self.__config_loader_thread = gevent.spawn(configLoaderLoop, self, CONFIG_LOAD_INTERVAL)
        if not self.__throttle:
            self.__update_log_thread    = gevent.spawn(updateLogLoop, self, UPDATE_LOG_INTERVAL)
            #self.startThreads()

    def updateDbLog(self):
        print('#### CALLING UPDATEDBLOG')
        callmap = dict()
        for k,v in self.__limiters:
            callmap[k] = v.day_calls
        self.__rllog.updateLog(callmap)

    def loadDbLog(self):
        callmap = self.__rllog.getLog()
        if callmap is None:
            return
        for k,v in callmap.iteritems():
            if k in self.__limiters:
                self.__limiters[k].day_calls = v

    def startThreads(self):
        if self.__config_loader_thread is None:
            self.__config_loader_thread = gevent.spawn(configLoaderLoop, self, CONFIG_LOAD_INTERVAL)
        if self.__update_log_thread is None:
            self.__update_log_thread    = gevent.spawn(updateLogLoop, self, UPDATE_LOG_INTERVAL)

    def stopThreads(self):
        if self.__config_loader_thread is not None:
            self.__config_loader_thread.kill()
            self.__config_loader_thread = None
        if self.__update_log_thread is not None:
            self.__update_log_thread.kill()
            self.__update_log_thread = None


    def loadLimiterConfig(self):
        filename = 'limits-%s.conf' % self.__stack_name
        limits_path = '%s/%s' % (LIMITS_DIR, filename)

        print('checking config file for updates.  path: %s' % limits_path)

        try:
            meta = {}
            if os.path.exists(limits_path):
                with open(limits_path, "rb") as fp:
                    source = fp.read()

                exec compile(source, limits_path, "exec") in meta
            else:
                print("### Could not find '%s': no limits defined" % filename)
                return
        except Exception as e:
            print("Exception while trying to execute '%s' file: %s" % (filename, e))
            return

        try:
            limits = meta['limits']
        except:
            print('limits var is not being set in config file.  skipping load step')
            return

        for k,v in limits.iteritems():
            service_name = None
            try:
                service_name    = k
                limit           = v.get('limit', None)
                period          = v.get('period', None)
                cpd             = v.get('cpd', None)
                fail_limit      = v.get('fail_limit', None)
                fail_period     = v.get('fail_period', None)
                blackout_wait   = v.get('blackout_wait', None)
                if self.__throttle:
                    # throttle qps to 1/10 the rate, and cpd to allow 1/10th the remaining calls in quota
                    if limit is not None:
                        limit = max(1, limit / 10)
                    if cps is not None:
                        day_calls = 0
                        if service_name in self.__limiters:
                            day_calls = self.__limiters[service_name].day_calls
                        cpd = min(cpd, day_calls + (cpd-day_calls) / 10)
            except Exception as e:
                if service_name is not None:
                    print ("Exception while reading limiter for service '%s' in limits config, skipping: %s" % (service_name, e))
                else:
                    print ('Exception while reading limiter in limits config, skipping')
                continue

            try:
                limiter = self.__limiters.get(service_name, None)
                if limiter is not None:
                    limiter.update_limits(limit, period, cpd, fail_limit, fail_period, blackout_wait)
                else:
                    print("adding rate limiter for service '%s'" % service_name)
                    self.__limiters[service_name] = RateLimiter(service_name, limit, period, cpd, fail_limit, fail_period, blackout_wait)
            except:
                print ("Exception thrown while attempting to update or create RateLimiter '%s'. Skipping" % service_name)
                return

    def handleRequest(self, service, priority, timeout, verb, url, body = {}, headers = {}):
        print ('calling exposed_request')
        if timeout is None:
            raise StampedInputError("Timeout period must be provided")
        request = Request(timeout, verb, url, body, headers)

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