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
import datetime
import traceback

from time               import time, gmtime, mktime
from collections        import deque

REQUEST_DUR_LOG_SIZE    = 10    # the size of the request duration log, which is used to determine the avg request duration
REQUEST_DUR_CAP         = 5.0   # the cap for an individual request duration when determining the avg request duration


#def schedulerLoop(limiter):
#    limit = limiter.__limit
#    period = limiter.period
#    while True:
#        calls = limiter.__limit_calls_remaining
#        sleep(period)
#
#    sleep()

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

class TooManyFailedRequestsException(Exception):
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

class DailyLimitException(RateException):
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


events = []


def workerProcess(limit):
    global events

    period = limit.period

    while True:
        if (len(events) > 0):
            for event in events:
                print(event)
            events = []
        limit.handleTimestep()
        if limit._isFailed():
            print('isFailed is true.  Sleeping for %s' % (limit.fail_wait - (time() - limit.fail_start)))
            gevent.sleep(limit.fail_wait - (time() - limit.fail_start))
        else:
            gevent.sleep(period)
        sleep(0)

class RateLimiter(object):

    def __init__(self, limit=None, period=None, cpd=None, fail_limit=None, fail_period=None, fail_wait=None):
        print('rate limit init')

        self.__requests = RLPriorityQueue()
        self.__http = httplib2.Http()

        self.limit = limit
        self.period = period
        self.__cpd = cpd
        self.__curr_timeblock_start =  time()

        self.__fails = deque()
        self.__fail_limit = fail_limit
        self.__fail_period = fail_period
        self.fail_wait = fail_wait
        self.fail_start = None

        self.__request_dur_log = deque()
        self.__request_dur_log_size = REQUEST_DUR_LOG_SIZE
        self.__request_dur_cap = REQUEST_DUR_CAP

        self.__calls = 0
        self.__day_calls = 0
        self.__day_start = self._getDay()

        self.__low_count = 0
        self.__high_count = 0

        self.__just_finished = 0

        self.__semaphore = Semaphore()

        self.__worker = gevent.spawn(workerProcess, self)

    def fail(self, now=None):
        if self.__fails is None:
            return

        if now is None:
            now = time()

        self.__semaphore.acquire()

        self.__fails.append(now)

        cutoff = now - self.__fail_period
        count = 0

        for timestamp in self.__fails:
            if timestamp > cutoff:
                count += 1
            else:
                self.__fails.popleft()

        self.__semaphore.release()


        if count > self.__fail_limit:
            print('### hit fail limit')
            self.fail_start = time()

    def call(self):
        self.__calls += 1
        self.__day_calls += 1


    def _isFailed(self, now=None):
        if now is None:
            now = time()

        if self.fail_start is None:
            return False
        if (now - self.fail_start) < self.fail_wait:
            return True

        self.fail_start = None
        return False

    def _isDayLimit(self):
        now = mktime(datetime.datetime.utcnow().timetuple())
        # reset counter if day has elapsed
        print('Day start: %s   now: %s' % (self.__day_start, now))
        if self.__day_start + 60*60*24 < now:
            self.__day_start = self._getDay()
            self.__day_calls = 0

        return self.__day_calls >= self.__cpd


    def _getDay(self):
        now = gmtime()
        return mktime(datetime.datetime(now.tm_year, now.tm_mon, now.tm_mday).timetuple())

    def _addDurationLog(self, elapsed):
        """
        Add the duration of the request to the request log for generating an average request time
        """
        self.__request_dur_log.append(elapsed)
        if len(self.__request_dur_log) > self.__request_dur_log_size:
            self.__request_dur_log.popleft()


    def _getRateWaitTime(self, now=None):
        if self.__calls < self.limit:
            return 0
        return self.period - (now - self.__curr_timeblock_start)

    def _getExpectedRequestTime(self):
        if len(self.__request_dur_log) == 0:
            return 0

        dur_sum = 0
        for dur in self.__request_dur_log:
            dur_sum += min(dur, self.__request_dur_cap)

        return dur_sum / len(self.__request_dur_log)

    def _getExpectedWaitTime(self, now, priority=0):
        # determine the longest wait time for all of the rate limits, given the number of items in the queue
        rate_wait = self._getRateWaitTime(now)
        num_pending_requests = self.__requests.qsize_priority(priority)
        queue_wait = (num_pending_requests / self.limit) * self.period

        return rate_wait + queue_wait

    def addRequest(self, request, priority):
        try:
            now = time()

            expected_request_time = self._getExpectedRequestTime()
            expected_wait_time = self._getExpectedWaitTime(now, priority)
            expected_total_time = expected_request_time + expected_wait_time
            request.log.expected_dur = expected_total_time

            if priority == 0 and expected_wait_time + expected_request_time > request.timeout:
                raise WaitTooLongException("Expected request time too long. Expected: %s Timeout: %s" %
                                           (expected_total_time + expected_request_time, request.timeout))

            if self._isFailed():
                raise TooManyFailedRequestsException("Too many failed requests. Wait time remaining: %s" %
                                                     (self.fail_wait - (now - self.fail_start)))
            if self._isDayLimit():
                raise DailyLimitException("Hit the daily request cap.  Wait time remaining: %s minutes" %
                                        (((self.__day_start + 60*60*24) - now) / 60))


            asyncresult = AsyncResult()

            if self.__curr_timeblock_start is None:
                self.__curr_timeblock_start = now
            if self.__calls < self.limit:
                self.call()
                self.doRequest(request, asyncresult)
            else:
                self.__requests.put((priority, request, asyncresult))
                print('queue_size: %s' % self.__requests.qsize())

            return asyncresult
        except Exception as e:
            print('### Exception: %s' % e)
            traceback.print_exc()
            raise e

    def handleTimestep(self):
        print('self.__requests.qsize: %s' % self.__requests.qsize())

        self.__calls = 0
        now = time()
        while (self.__curr_timeblock_start + self.period < now):
            self.__curr_timeblock_start += self.period  # TODO convert seconds to timedelta
        while self.__calls < self.limit:
            try:
                (priority, request, asyncresult) = self.__requests.get(block=False)
                self.call()
                gevent.spawn(self.doRequest, request, asyncresult)
            except gevent.queue.Empty: # TODO FIND RIGHT EXCEPTION HERE
                break

    def doRequest(self, request, asyncresult):
        global events

        begin = time()

        if (begin - request.created) > request.timeout:
            print('timeout exceptions thrown')
            raise TimeoutException('The request timed out while waiting in the rate limiter queue')

        events.append('sending out http request')
        try:
            response, content = self.__http.request(request.url, request.verb, headers=request.headers, body=urllib.urlencode(request.body))
        except Exception as e:
            events.append('Exception during request: %s' % e)
            print('Exception during request: %s' % e)
            asyncresult.set_exception(e)
            raise e
        if response.status >= 400:
            self.fail()

        events.append('setting asyncresult with http response, content')
        asyncresult.set((response, content))

        end = time()
        elapsed = end - begin
        realized_dur = end - request.created
        events.append('realized dur: %s  expected dur: %s' % (realized_dur, request.log.expected_dur))
        print('realized dur: %s  expected dur: %s' % (realized_dur, request.log.expected_dur))

        events.append('adding duration log')
        self._addDurationLog(elapsed)

        return response, content