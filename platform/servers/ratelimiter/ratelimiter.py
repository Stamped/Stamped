#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import gevent
from gevent             import monkey
monkey.patch_all()
from GreenletServer     import GreenletServer
from gevent.queue       import PriorityQueue
from gevent.event       import AsyncResult
from gevent.coros       import Semaphore
from rpyc.utils.server  import ThreadedServer

import Globals
import rpyc
import urllib
import httplib2
from time               import time, sleep
from collections        import deque

from errors             import *

REQUEST_DUR_LOG_SIZE    = 10    # the size of the request duration log, which is used to determine the avg request duration
REQUEST_DUR_CAP         = 5.0   # the cap for an individual request duration when determining the avg request duration

from optparse           import OptionParser
#from libs.RateLimiter import RateLimiter

class RateException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)
        print(msg)

class RateLimitExceededException(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)
        print(msg)

class WaitTooLongException(RateException):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)
        print(msg)

class TimeoutException(RateException):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)
        print(msg)

class RequestLog():
    def __init__(self):
        self.avg_wait_time = None
        self.max_wait = 0
        self.expected_wait = None
        self.items_in_queue = 0

class Request():
    def __init__(self, timeout, verb, url, body, headers):
        self.created = time()
        self.timeout = timeout
        self.verb = verb
        self.url = url
        self.body = body
        self.headers = headers
        self.log = RequestLog()

class RateLimit(object):
    def __init__(self, limit, duration):
        if limit is None:
            raise ValueError('limit must be a non-negative number, not None')

        if limit < 0:
            raise ValueError('limit must be >= 0')

        self.__limit    = limit
        self.__duration = duration
        self.__calls    = 0
        self.__start    = time()

    def __update(self, now=None):
        if now is None:
            now = time()

        diff = now - self.__start

        if diff >= self.__duration:
            self.__start = now
            self.__calls = 0

    def call(self, now=None):
        self.__update(now)
        self.__calls += 1

    def wait(self, now=None):
        if now is None:
            now = time()

        self.__update(now)

        if self.__calls >= self.__limit:
            diff = now - self.__start
            return self.__duration - diff
        else:
            return 0

# Fail Limit functions similarly to RateLimit, but only initiates a wait period once the fail limit has been reached
# The cool down field is used to impose a stricter fail trigger immediately after resetting from a failure timeout:
#  Every failed request decrements cooldown, and every success increments cooldown.  When cooldown hits 0, a wait period
#  is enforced as if a fail limit were hit. After resetting from a wait, cooldown is set to 1 so that if we immediately
#  hit an error, a wait period will be imposed again.
class FailLimit(object):


    def __init__(self, limit, duration):
        if limit is None:
            raise ValueError('limit must be a non-negative number, not None')

        if limit < 0:
            raise ValueError('limit must be >= 0')

        self.__limit    = limit
        self.__duration = duration
        self.__fails    = 0
        self.__start    = None
        self.__cooldown = 0

    def __update(self, now=None):
        if self.__start is None:
            return

        if now is None:
            now = time()

        diff = now - self.__start

        if diff >= self.__duration:
            self.__start = None
            self.__fails = 0
            self.__cooldown = 1

    def fail(self, now=None):
        self.__update(now)
        self.__fails += 1
        self.__cooldown -= 1

        if self.__fails >= self.__limit or self.__cooldown == 0:
            self.__start = time()

    def success(self, now=None):
        self.__cooldown += 1

    def wait(self, now=None):
        if self.__start is None:
            return 0

        if now is None:
            now = time()

        self.__update(now)

        if self.__start is None:
            return 0
        else:
            diff = now - self.__start
            return self.__duration - diff


def processRequestLoop(limiter):
    print('### starting up processRequestLoop')
    while True:
        limiter.doRequest()

class RateLimiter(object):

    def __init__(self, cps=None, cpm=None, cph=None, cpd=None, fail_limit=None, fail_dur=None, max_wait=None):
        print('rate limit init')
        self.__queue = gevent.queue.PriorityQueue()
        self.__max_wait = max_wait
        self.__limits = {}
        self.__fail_limit = None
        self.__fails = 0
        self.__request_dur_log = deque()
        self.__http = httplib2.Http()
        self.__request_dur_log_size = REQUEST_DUR_LOG_SIZE
        self.__request_dur_cap = REQUEST_DUR_CAP

        if cps is not None and cps != 0:
            self.__limits['calls per second'] = RateLimit(cps, 1)

        if cpm is not None and cpm != 0:
            self.__limits['calls per minute'] = RateLimit(cpm, 60)

        if cph is not None and cph != 0:
            self.__limits['calls per hour'] = RateLimit(cph, 60*60)

        if cpd is not None and cpd != 0:
            self.__limits['calls per day'] = RateLimit(cpd, 60*60*24)

        if fail_limit is not None and fail_dur is not None:
            self.__fail_limit = FailLimit(fail_limit, fail_dur)

        self.__semaphore = Semaphore()
        self.__workers = [gevent.spawn(processRequestLoop, self) for i in range(10 if cps is None else min(cps,20))]

    def _addDurationLog(self, elapsed, total_waited, total_elapsed):
        """
        Add the duration of the request to the request log for generating an average request time
        """
        self.__request_dur_log.append(elapsed)
        if len(self.__request_dur_log) > self.__request_dur_log_size:
            self.__request_dur_log.popleft()

    def _getLimitsWait(self, now):
        """
        Get the longest wait time among rate limits and the fail limit
        """
        max_wait = 0
        max_name = None

        for name, limit in self.__limits.items():
            wait = limit.wait(now)

            if wait > max_wait:
                max_name = name
                max_wait = wait

        if self.__fail_limit is not None:
            fail_wait = self.__fail_limit.wait(now)
            if fail_wait > max_wait:
                max_wait = fail_wait
                max_name = 'fail limit'

        return max_wait, max_name

    def _getAverageRequestTime(self):
        if len(self.__request_dur_log) == 0:
            return 0

        dur_sum = 0
        for dur in self.__request_dur_log:
            dur_sum += min(dur, self.__request_dur_cap)

        return dur_sum / len(self.__request_dur_log)

    def _getExpectedWait(self, now, request=None):
        # Calculate wait time based on average req time wait * num pending requests plus the current rate limit wait
        avg = self._getAverageRequestTime()
        max_wait, max_name = self._getLimitsWait(now)
        expected_wait = max_wait + (self.__queue.qsize() * avg)

        # add to request log
        if request is not None:
            request.log.avg_wait_time = avg
            request.log.max_wait = max_wait
            request.log.items_in_queue = self.__queue.qsize()
            request.log.expected_wait = expected_wait

        return expected_wait

    def _enforceWait(self):
        locked = self.__semaphore.acquire(timeout=self.__max_wait)
        if locked:
            try:
                now = time()

                max_wait, max_name = self._getLimitsWait(now)

                if self.__max_wait is not None and max_wait > self.__max_wait:
                    raise RateLimitExceededException('Rate limit exceeded for service: %s' % max_name)

                if max_wait > 0:
                    end = now + max_wait

                    while True:
                        cur = time()
                        if cur >= end:
                            break
                        else:
                            sleep(end - cur)

                for name, limit in self.__limits.items():
                    wait = limit.wait()
                    if wait > 0:
                        logs.warning('%s wait should be 0 is %s' % (name, wait))

                    limit.call()
            finally:
                self.__semaphore.release()
        else:
            raise RateException('Max wait (%s) exceeded trying to get slot' % self.__max_wait)


    def addRequest(self, request, priority="high"):
        now = time()

        priority_int = 0
        if priority == "low":
            priority_int = 10

        if priority_int == 0 and self._getExpectedWait(now, request) > request.timeout:
            max_wait, max_name = self._getLimitsWait(now)
            raise WaitTooLongException("Expected wait too long: %s seconds   TIMEOUT: %s  MAX LIMIT '%s':  %s" %
                                       (self._getExpectedWait(now, request), request.timeout, max_name, max_wait))
        asyncresult =  AsyncResult()

        data = (priority_int, request, asyncresult)
        self.__queue.put(data)
        return asyncresult

    def doRequest(self):
        priority, request, asyncresult = self.__queue.get()

        if (request.created + request.timeout < time()):
            #TODO: add timeout log
            asyncresult.set(TimeoutException("Timeout Exception"))
            return

        begin = time()
        self._enforceWait()
        total_wait = time() - request.created
        log = request.log
        if log is not None:
            print( 'realized wait: %s    expected wait: %s  max_wait: %s  avg_wait_time: %s  items in queue: %s  priority: %s' %
                   (total_wait, log.expected_wait, log.max_wait, log.avg_wait_time, log.items_in_queue, priority))
        try:
            response, content = self.__http.request(request.url, request.verb, headers=request.headers, body=urllib.urlencode(request.body))
        except Exception as e:
            asyncresult.set_exception(e)
            return
        if self.__fail_limit is not None:
            if response.status >= 400:
                self.__fail_limit.fail()
            else:
                self.__fail_limit.success()

        print('### response: %s' % response)
        asyncresult.set((response, content))
        now = time()
        elapsed = now - begin
        total_elapsed = now - request.created
        self._addDurationLog(elapsed, total_wait, total_elapsed)
        return

limiters = {
    'facebook'      : RateLimiter(                      fail_limit=10,      fail_dur=60),
    'twitter'       : RateLimiter(                      fail_limit=10,      fail_dur=60),
    'netflix'       : RateLimiter(cps=4,    cpd=100000, fail_limit=10,      fail_dur=60),
    'rdio'          : RateLimiter(          cpd=15000,  fail_limit=10,      fail_dur=60),
    'spotify'       : RateLimiter(                      fail_limit=10,      fail_dur=60),
    }


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
        if timeout is None:
            raise StampedInputError("Timeout period must be provided")
        request = Request(timeout, verb, url, body, headers)

        limiter = limiters[service]

        asyncresult = limiter.addRequest(request, priority)

        # This sleep call is necessary because of a bug with the way gevent handles timeouts... Effectively resets
        # the starting time for the timeout, otherwise the starting time is the time of last pop from queue
        gevent.sleep(0)
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
