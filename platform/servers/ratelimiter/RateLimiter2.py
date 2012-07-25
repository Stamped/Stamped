import gevent
from gevent import monkey
monkey.patch_all()
from gevent             import sleep
from gevent.queue       import PriorityQueue
from gevent.event       import AsyncResult
from gevent.coros       import Semaphore

import Globals
import logs
import urllib
import httplib2
import datetime
import traceback

import utils

import calendar, time
from collections        import deque

from django.utils.html  import escape
from libs.ec2_utils     import is_ec2, get_stack

REQUEST_DUR_LOG_SIZE    = 10    # the size of the request duration log, which is used to determine the avg request duration
REQUEST_DUR_CAP         = 10.0   # the cap for an individual request duration when determining the avg request duration



events = []

class RLPriorityQueue(PriorityQueue):
    def qsize_priority(self, priority):
        """ Return the number of entries in the queue of equal or higher priority.  Assumes the entries are a sequence
            where the first index is the priority as int
        """
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
        self.expected_request_time = 0
        self.expected_wait_time = 0
        self.expected_dur = None
        self.items_in_queue = 0
        self.count = 0

class Request():
    def __init__(self, timeout, verb, url, body, headers):
        self.created = time.time()
        self.timeout = timeout
        self.verb = verb
        self.url = url
        self.body = body
        self.headers = headers
        self.log = RequestLog()

def workerProcess(limit):
    period = limit.period

    while True:
        limit.handleTimestep()
        if limit._isBlackout():
            print('Fail limit reached.  Sleeping for %s' % (limit.blackout_wait - (time.time() - limit.blackout_start)))
            gevent.sleep(limit.blackout_wait - (time.time() - limit.blackout_start))
        else:
            gevent.sleep(period)
        sleep(0)

def printProcess(limit):
    global events

    while True:
        sleep(10)
        for e in events:
            print e
        events = []


class RateLimiter(object):

    def __init__(self, service_name=None, limit=None, period=None, cpd=None, fail_limit=None, fail_period=None, blackout_wait=None):
        self.__service_name = service_name
        self.__requests = RLPriorityQueue()

        self.count = 0

        self.limit = limit
        self.period = period
        self.cpd = cpd
        self.__curr_timeblock_start =  time.time()

        self.__fails = deque()
        self.fail_limit = fail_limit
        self.fail_period = fail_period
        self.blackout_wait = blackout_wait
        self.blackout_start = None

        self.__request_dur_log = deque()
        self.__request_dur_log_size = REQUEST_DUR_LOG_SIZE
        self.__request_dur_cap = REQUEST_DUR_CAP

        self.__calls = 0
        self.day_calls = 0
        self.__day_start = self._getDay()

        self.__low_count = 0
        self.__high_count = 0

        self.__just_finished = 0

        self.__semaphore = Semaphore()
        self.__queue_sem = Semaphore()

        if self.limit is not None and self.period is not None:
            self.__worker = gevent.spawn(workerProcess, self)

        gevent.spawn(printProcess, self)

    def update_limits(self, limit, period, cpd, fail_limit, fail_period, blackout_wait):
        if self.limit != limit:
            self.limit = limit
        if self.period != period:
            self.period = period
        if self.cpd != cpd:
            self.cpd = cpd
        if self.fail_limit != fail_limit:
            self.fail_limit = fail_limit
        if self.fail_period != fail_period:
            self.fail_period = fail_period
        if self.blackout_wait != blackout_wait:
            self.blackout_wait = blackout_wait

    class FailLog(object):
        def __init__(self, url, body, headers, status_code, content):
            self.url = url
            self.body = body
            self.headers = headers
            self.timestamp = time.time()
            self.status_code = status_code
            self.content = content

    def sendFailLogEmail(self):
        if len(self.__fails) == 0:
            return

        stack_info = get_stack()
        stack_name = 'localhost'
        node_name = 'localhost'
        if stack_info is not None:
            stack_name = stack_info.instance.stack
            node_name = stack_info.instance.name

        output = '<html>'
        output += "<h3>RateLimiter Fail Limit reached</h3>"
        output += "<p>On stack '%s' instance '%s'.</p>" % (stack_name, node_name)
        output += "<p><i>There were %s failed requests to service '%s' within the last %s seconds</p></i>" %  \
                  (self.fail_limit, self.__service_name, self.fail_period)
        back_online = time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(self.blackout_start + self.blackout_wait)) # Timestamp
        output += "<p>Waiting for %s seconds.  Service will be active again at: %s</p>" % (self.blackout_wait, back_online)

        output += '<h3>Fail Log</h3>'

        output += '<table border=1 cellpadding=5>'
        output += '<tr>'
        labels = ['Timestamp', 'Url', 'Body', 'Headers', 'Code', 'Content']
        for label in labels:
            output += '<td style="font-weight:bold">%s</td>' % label
        output += '</tr>'

        for fail in self.__fails:
            output += '<tr>'
            output += '<td valign=top>%s</td>' % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(fail.timestamp)) # Timestamp
            output += '<td valign=top>%s</td>' % fail.url
            output += '<td valign=top>%s</td>' % fail.body
            output += '<td valign=top>%s</td>' % fail.headers
            output += '<td valign=top>%s</td>' % fail.status_code
            output += '<td valign=top>%s</td>' % escape(fail.content)
            output += '</tr>'

        output += '</table>'
        output += '</html>'

        try:
            email = {}
            email['from'] = 'Stamped <noreply@stamped.com>'
            email['to'] = 'mike@stamped.com'
            email['subject'] = "RateLimiter '%s' fail limit reached" % self.__service_name
            email['body'] = output
            utils.sendEmail(email, format='html')
        except Exception as e:
            print('UNABLE TO SEND EMAIL: %s' % e)

        return output

    def fail(self, request, response, content):
        if self.fail_limit is None or self.fail_period is None or self.blackout_wait is None:
            return

        now = time.time()

        ### Was getting deque() corruption error when the server was uploaded with requests.  This is to help prevent that.
        self.__semaphore.acquire()

        self.__fails.append(self.FailLog(request.url, request.body, request.headers, response.status, content))

        cutoff = now - self.fail_period
        count = 0

        while len(self.__fails) > 0:
            if self.__fails[0].timestamp < cutoff:
                self.__fails.popleft()
            else:
                break
        count = len(self.__fails)

        self.__semaphore.release()

        if count > self.fail_limit:
            logs.warning("hit fail limit for service '%s'" % self.__service_name)
            self.blackout_start = time.time()

            # Email dev if a fail limit was reached
            if is_ec2():
                self.sendFailLogEmail()

    def call(self):
        self.__calls += 1
        self.day_calls += 1


    def _isBlackout(self, now=None):
        if now is None:
            now = time.time()

        if self.blackout_start is None:
            return False
        if (now - self.blackout_start) < self.blackout_wait:
            return True

        self.blackout_start = None
        return False

    def _isDayLimit(self):
        """ Check if we have gone over the daily rate limit. We compare the current utc time against the
            end of the utc day and reset the counters when the day has elapsed
        """
        if self.cpd is None:
            return False

        now = calendar.timegm(time.gmtime())
        if self.__day_start + 60*60*24 < now:
            print('day elapsed')
            self.__day_start = self._getDay()
            self.day_calls = 0

        return self.day_calls >= self.cpd


    def _getDay(self):
        """ Get beginning of current utc day in seconds since the epoch
        """
        now = datetime.datetime.utcnow()
        date = datetime.datetime(now.year, now.month, now.day)
        return calendar.timegm(date.timetuple())

    def _addDurationLog(self, elapsed):
        """ Add the duration of the request to the request log for generating an average request time
        """
        self.__request_dur_log.append(elapsed)
        if len(self.__request_dur_log) > self.__request_dur_log_size:
            self.__request_dur_log.popleft()


    def _getRateWaitTime(self, now=None):
        if self.limit is None or self.period is None:
            return 0
        if self.__calls < self.limit:
            return 0
        return max(0, self.period - (now - self.__curr_timeblock_start))

    def _getExpectedRequestTime(self):
        if len(self.__request_dur_log) == 0:
            return 0

        dur_sum = 0
        for dur in self.__request_dur_log:
            dur_sum += min(dur, self.__request_dur_cap)

        return max(0, dur_sum / len(self.__request_dur_log))

    def _getExpectedWaitTime(self, now, priority):
        ### determine the longest wait time for all of the rate limits, given the number of items in the queue
        ###
        if self.limit is None or self.period is None:
            return 0
        rate_wait = self._getRateWaitTime(now)
        num_pending_requests = self.__requests.qsize_priority(priority)
        queue_wait = (num_pending_requests / self.limit) * self.period

#        print('rate_wait: %s queue_wait: %s' % (rate_wait, queue_wait))

        return rate_wait + queue_wait

    def addRequest(self, request, priority):
        global events
        request.log.count = self.count
        self.count += 1
        try:
            now = time.time()

            expected_request_time = self._getExpectedRequestTime()
            expected_wait_time = self._getExpectedWaitTime(now, priority)
            expected_total_time = expected_request_time + expected_wait_time
            request.log.expected_wait_time = expected_wait_time
            request.log.expected_request_time = expected_request_time
            request.log.expected_dur = expected_total_time
            request.log.items_in_queue = self.__requests.qsize_priority(priority)

#            events.append('Service: %s  Request %s:   Received request' %
#                          (self.__service_name, request.log.count))

            if priority == 0 and self.__requests.qsize() > 0 and \
               (expected_wait_time + expected_request_time) > request.timeout:
                raise WaitTooLongException("Expected request time too long. Expected: %s Timeout: %s" %
                                           (expected_total_time + expected_request_time, request.timeout))

            if self._isBlackout():
                raise TooManyFailedRequestsException("Too many failed requests. Wait time remaining: %s seconds" %
                                                     (self.blackout_wait - (now - self.blackout_start)))
            if self._isDayLimit():
                raise DailyLimitException("Hit the daily request cap.  Wait time remaining: %s minutes" %
                                        (((self.__day_start + 60*60*24) - now) / 60))

            asyncresult = AsyncResult()

            if self.__curr_timeblock_start is None:
                self.__curr_timeblock_start = now
            if self.limit is None or self.period is None or self.__calls < self.limit:

#                events.append('Service: %s  Request %s:   calls: %s is < limit: %s Making request Immediately' %
#                              (self.__service_name, request.log.count, self.__calls, self.limit))
                self.call()
                self.doRequest(request, asyncresult)
            else:
                events.append('Service: %s  Request %s:   Adding request to queue' %
                              (self.__service_name, request.log.count))
                self.__requests.put((priority, request, asyncresult))

            #                print('queue_size: %s' % self.__requests.qsize())

            return asyncresult
        except Exception as e:
#            events.append('Service: %s  Request %s:   addRequest threw exception: %s' % (self.__service_name, request.log.count, e))
            logs.error('addRequest threw exception: %s' % e)
            traceback.print_exc()
            raise e

    def handleTimestep(self):
        global events
        self.__calls = 0
        now = time.time()
        while (self.__curr_timeblock_start + self.period < now):
            self.__curr_timeblock_start += self.period  # TODO convert seconds to timedelta
        requests = []

        while self.__calls < self.limit:
            try:
                requests.append(self.__requests.get(block=False))
                events.append('Service: %s  Request %s:   Pulled from queue' %
                              (self.__service_name, requests[-1][1].log.count))
                self.call()
            except gevent.queue.Empty:
                break

        for priority, request, asyncresult in requests:
            events.append('Service: %s  Request %s:   Spawning doRequest thread' %
                          (self.__service_name, request.log.count))
            gevent.spawn(self.doRequest, request, asyncresult)

    def doRequest(self, request, asyncresult):
        global events
        try:
            begin = time.time()
            http = httplib2.Http()

            if (begin - request.created) > request.timeout:
#                events.append('Service: %s  Request %s:   Throwing TimeoutException.  realized wait: %s  '
#                              'expected dur: %s  items originally in queue: %s' %
#                              (self.__service_name, request.log.count, begin - request.created, request.log.expected_dur, request.log.items_in_queue))
                raise TimeoutException('The request timed out while waiting in the rate limiter queue.'
                                       'Expected time: %s  Items in queue: %s  Realized time: %s  Service: %s' %
                                        (request.log.expected_dur, request.log.items_in_queue, begin - request.created,
                                         self.__service_name))

            body = None
            if request.body is not None:
                body = urllib.urlencode(request.body, True)
#            events.append('Service: %s  Request %s:   Making request.  Realized wait %s' %
#                          (self.__service_name, request.log.count, begin - request.created))
            response, content = http.request(request.url, request.verb, headers=request.headers, body=body)
            if response.status >= 400:
                self.fail(request, response, content)

            asyncresult.set((response, content))

            end = time.time()
            elapsed = end - begin
            realized_dur = end - request.created


#            events.append('Service: %s  Request %s:   Request finished.  Request time: %s  Realized total time: %s  '
#                          'Expected Total Time: %s  Expected wait time: %s  Expected request time: %s  Items originally in Queue: %s' %
#                          (self.__service_name, request.log.count, elapsed, realized_dur,
#                           request.log.expected_dur, request.log.expected_wait_time, request.log.expected_request_time,
#                              request.log.items_in_queue))


#            print("service: %s  realized dur: %s  expected dur: %s  expected wait: %s  expected request time: %s  queue size: %s" %
#                  (self.__service_name, realized_dur, request.log.expected_dur, request.log.expected_wait_time,
#                   request.log.expected_request_time, request.log.items_in_queue), )

            self._addDurationLog(elapsed)

            return response, content
        except Exception as e:
            print('Exception in doRequest: %s' % ''.join(traceback.format_exc()))
            asyncresult.set_exception(e)
            raise e

