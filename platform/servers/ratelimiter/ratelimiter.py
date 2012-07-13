#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import gevent
from gevent import monkey
monkey.patch_all()
from gevent             import sleep
from gevent.queue       import PriorityQueue
from gevent.event       import AsyncResult
from gevent.coros       import Semaphore

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

class RLPriorityQueue(PriorityQueue):
    def qsize_priority(self, priority):
        """Return the number of entries in the queue of equal or higher priority.  Assumes the entries are a sequence
           where the first index is the priority as int"""
        count = 0
        for item in self.queue:
            if item[0] <= priority:
                count += 1
        return count

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
        self.expected_dur = None
        self.items_in_queue = 0

class Request():
    def __init__(self, timeout, verb, url, body, headers):
        self.number = 0
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

    def wait_forecast(self, num_requests, now=None):
        if now is None:
            now = time()
        wait = self.wait(now)

        # if the wait time is in effect, then it will clear the number of calls in RateLimit afterward
        cur_calls = self.__calls
        if wait > 0:
            cur_calls = 0

        requests_wait = ((num_requests + cur_calls) / self.__limit) * self.__duration
        return wait + requests_wait

# Fail Limit functions similarly to RateLimit, but only initiates a wait period once the fail limit has been reached
# The cool down field is used to impose a stricter fail trigger immediately after resetting from a failure timeout:
#  Every failed request decrements cooldown, and every success increments cooldown.  When cooldown hits 0, a wait period
#  is enforced as if a fail limit were hit. After resetting from a wait, cooldown is set to 1 so that if we immediately
#  hit an error, a wait period will be imposed again.
class FailLimit(object):


    def __init__(self, limit, limit_dur, wait_dur):
        if limit is None:
            raise ValueError('limit must be a non-negative number, not None')

        if limit < 0:
            raise ValueError('limit must be >= 0')

        self.__limit    = limit
        self.__wait_duration = wait_dur
        self.__limit_duration = limit_dur
        self.__fails    = deque()
        self.__start    = None
        #self.__cooldown = 0

    def __update(self, now=None):
        if self.__start is None:
            return

        if now is None:
            now = time()

        diff = now - self.__start

        if diff >= self.__wait_duration:
            self.__start = None
            self.__fails.clear()
            #self.__cooldown = 1

    def fail(self, now=None):
        if now is None:
            now = time()

        self.__update(now)
        self.__fails.append(now)
        #self.__cooldown -= 1


        cutoff = now - self.__limit_duration
        count = 0
        for timestamp in self.__fails:
            if timestamp > cutoff:
                count += 1
            else:
                self.__fails.popleft()

        if count > self.__limit:
            print('### hit fail limit')
            self.__start = time()

#        if self.__fails >= self.__limit or self.__cooldown == 0:
#            self.__start = time()

    def success(self, now=None):
        pass
        #self.__cooldown += 1

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
            return self.__wait_duration - diff



def wakerLoop(limiter):
    limit = limiter.getRateLimit
    dur = limiter.getRateDur()

    while True:
        if

def processRequestLoop(limiter):
    print('### starting up processRequestLoop')
    while True:
        limiter.doRequest()

count = 0

class RateLimiter(object):

    def __init__(self, cps=None, cpm=None, cph=None, cpd=None, fail_limit=None, limit_dur=None, wait_dur=None, max_wait=None):
        print('rate limit init')
        self.__queue = RLPriorityQueue()
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

        if fail_limit is not None and wait_dur is not None and limit_dur is not None:
            self.__fail_limit = FailLimit(fail_limit, limit_dur, wait_dur)

        self.__semaphore = Semaphore()
        self.__waker = gevent.spawn(wakerLoop, self)
        self.__workers = [gevent.spawn(processRequestLoop, self) for i in range(10 if cps is None else min(cps*2,20))]

#    def wait(self):
#        while self.__semaphore.locked():
#            sleep(1)

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

    def _getExpectedWaitTime(self, now, priority=0):
        # determine the longest wait time for all of the rate limits, given the number of items in the queue
        max_wait = 0
        num_pending_requests = self.__queue.qsize_priority(priority)
        for name, limit in self.__limits.items():
            queue_wait = limit.wait_forecast(num_pending_requests, now)
            if queue_wait > max_wait:
                max_wait = queue_wait

        return max_wait

    def _getExpectedRequestTime(self, now, priority, request=None):
        # Calculate wait time based on average req time wait * num pending requests plus the current rate limit wait
        avg = self._getAverageRequestTime()
        max_wait, max_name = self._getLimitsWait(now)

        # expected request time equals the expected wait until request + the average request time
        # the expected wait until request is equal to the current max wait un
        expected_wait = self._getExpectedWaitTime(now, priority)

        total_wait = expected_wait + avg

        # add to request log
        if request is not None:
            request.log.avg_wait_time = avg
            request.log.max_wait = max_wait
            request.log.items_in_queue = self.__queue.qsize_priority(priority)
            request.log.expected_dur = total_wait

        print('### expected request time: %s' % total_wait)

        return total_wait

#    def _enforceWait(self):
        #locked = self.__semaphore.acquire(timeout=self.__max_wait)
#        if locked:
#            try:
#                now = time()
#
#                max_wait, max_name = self._getLimitsWait(now)
#
#                if self.__max_wait is not None and max_wait > self.__max_wait:
#                    raise RateLimitExceededException('Rate limit exceeded for service: %s' % max_name)
#
#                if max_wait > 0:
#                    end = now + max_wait
#
#                    while True:
#                        cur = time()
#                        if cur >= end:
#                            break
#                        else:
#                            sleep(end - cur)
#
#                for name, limit in self.__limits.items():
#                    wait = limit.wait()
#                    if wait > 0:
#                        logs.warning('%s wait should be 0 is %s' % (name, wait))
#
#                    limit.call()
#            #finally:
#                #self.__semaphore.release()
#        else:
#            raise RateException('Max wait (%s) exceeded trying to get slot' % self.__max_wait)



    def addRequest(self, request, priority="high"):
        global count

        now = time()

        priority_int = 0
        if priority == "low":
            priority_int = 10

        if priority_int == 0 and self._getExpectedRequestTime(now, priority_int, request) > request.timeout:
            max_wait, max_name = self._getLimitsWait(now)
            raise WaitTooLongException("Expected wait too long: %s seconds   TIMEOUT: %s  MAX LIMIT '%s':  %s" %
                                       (self._getExpectedRequestTime(now, priority_int, request), request.timeout, max_name, max_wait))
        asyncresult =  AsyncResult()


        #add to request queue


        #print('ADDING NUMBER: %s' % count)
        request.number = count
        count += 1
        data = (priority_int, request, asyncresult)

        self.__queue.put(data)
        return asyncresult

    def doRequest(self):
        priority, request, asyncresult = self.__queue.get()
        sleep(self._getExpectedWaitTime(begin, priority))
        for name, limit in self.__limits.items():
            limit.call()

        print ('READ NUM: %s' % request.number)

        if (request.created + request.timeout < time()):
            #TODO: add timeout log
            asyncresult.set(TimeoutException("Timeout Exception"))
            return

        begin = time()

        log = request.log
        try:
            response, content = self.__http.request(request.url, request.verb, headers=request.headers, body=urllib.urlencode(request.body))
        except Exception as e:
            asyncresult.set_exception(e)
            return

        realized_dur = time() - request.created

        if log is not None:
            print( 'NUM: %s  realized dur: %s    expected dur: %s  max_wait: %s  avg_wait_time: %s  items in queue: %s  priority: %s' %
                   (request.number, realized_dur, log.expected_dur, log.max_wait, log.avg_wait_time, log.items_in_queue, priority))


        if self.__fail_limit is not None:
            if response.status >= 400:
                self.__fail_limit.fail()
            else:
                self.__fail_limit.success()

        asyncresult.set((response, content))
        now = time()
        elapsed = now - begin
        total_elapsed = now - request.created
        self._addDurationLog(elapsed, total_wait, total_elapsed)
        return
