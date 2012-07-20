import gevent
from gevent import monkey
monkey.patch_all()
from gevent             import sleep
from gevent.queue       import PriorityQueue
from gevent.event       import AsyncResult
from gevent.coros       import Semaphore

import Globals
import urllib
import httplib2
import datetime
import traceback

import utils

import calendar
from time               import time, gmtime, mktime, strftime, localtime
from collections        import deque

from django.utils.html  import escape
from libs.ec2_utils     import is_ec2

REQUEST_DUR_LOG_SIZE    = 10    # the size of the request duration log, which is used to determine the avg request duration
REQUEST_DUR_CAP         = 10.0   # the cap for an individual request duration when determining the avg request duration


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
        self.max_wait = 0
        self.expected_dur = None
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

def workerProcess(limit):
    period = limit.period

    while True:
        limit.handleTimestep()
        if limit._isBlackout():
            print('Fail limit reached.  Sleeping for %s' % (limit.blackout_wait - (time() - limit.blackout_start)))
            gevent.sleep(limit.blackout_wait - (time() - limit.blackout_start))
        else:
            gevent.sleep(period)
        sleep(0)


class RateLimiter(object):

    def __init__(self, service_name=None, limit=None, period=None, cpd=None, fail_limit=None, fail_period=None, blackout_wait=None):
        self.__service_name = service_name
        self.__requests = RLPriorityQueue()

        self.limit = limit
        self.period = period
        self.cpd = cpd
        self.__curr_timeblock_start =  time()

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

        if self.limit is not None and self.period is not None:
            self.__worker = gevent.spawn(workerProcess, self)

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
        def __init__(self, status_code, content):
            self.timestamp = time()
            self.status_code = status_code
            self.content = content

    def sendFailLogEmail(self):
        if len(self.__fails) == 0:
            return

        output = '<html>'
        output += "<h3>RateLimiter Fail Limit reached</h3>"
        output += "<p><i>There were %s failed requests to service '%s' within the last %s seconds</p></i>" %  \
                  (self.fail_limit, self.__service_name, self.fail_period)
        back_online = strftime('%m/%d/%Y %H:%M:%S', localtime(self.blackout_start + self.blackout_wait)) # Timestamp
        output += "<p>Waiting for %s seconds.  Service will be active again at: %s</p>" % (self.blackout_wait, back_online)

        output += '<h3>Fail Log</h3>'

        output += '<table border=1 cellpadding=5>'
        output += '<tr>'
        labels = ['Timestamp', 'Code', 'Content']
        for label in labels:
            output += '<td style="font-weight:bold">%s</td>' % label
        output += '</tr>'

        for fail in self.__fails:
            output += '<tr>'
            output += '<td valign=top>%s</td>' % strftime('%m/%d/%Y %H:%M:%S', localtime(fail.timestamp)) # Timestamp
            output += '<td valign=top>%s</td>' % fail.status_code
            output += '<td valign=top>%s</td>' % escape(fail.content)
            output += '</tr>'

        output += '</table>'
        output += '</html>'

        try:
            email = {}
            email['from'] = 'Stamped <noreply@stamped.com>'
            email['to'] = 'dev@stamped.com'
            email['subject'] = "RateLimiter '%s' fail limit reached" % self.__service_name
            email['body'] = output
            utils.sendEmail(email, format='html')
        except Exception as e:
            print('UNABLE TO SEND EMAIL: %s' % e)

        return output

    def fail(self, response, content):
        if self.fail_limit is None or self.fail_period is None or self.blackout_wait is None:
            return

        now = time()

        ### Was getting deque() corruption error when the server was uploaded with requests.  This is to help prevent that.
        self.__semaphore.acquire()

        self.__fails.append(self.FailLog(response.status, content))

        cutoff = now - self.fail_period
        count = 0

        for log in self.__fails:
            if log.timestamp > cutoff:
                count += 1
            else:
                self.__fails.popleft()

        self.__semaphore.release()

        if count > self.fail_limit:
            print('### hit fail limit')
            self.blackout_start = time()

            # Email dev if a fail limit was reached
            if is_ec2():
                self.sendFailLogEmail()

    def call(self):
        self.__calls += 1
        self.day_calls += 1


    def _isBlackout(self, now=None):
        if now is None:
            now = time()

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

        now = calendar.timegm(gmtime())
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
        return self.period - (now - self.__curr_timeblock_start)

    def _getExpectedRequestTime(self):
        if len(self.__request_dur_log) == 0:
            return 0

        dur_sum = 0
        for dur in self.__request_dur_log:
            dur_sum += min(dur, self.__request_dur_cap)

        return dur_sum / len(self.__request_dur_log)

    def _getExpectedWaitTime(self, now, priority=0):
        ### determine the longest wait time for all of the rate limits, given the number of items in the queue
        ###
        if self.limit is None or self.period is None:
            return 0
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

            if priority == 0 and self.__requests.qsize() > 0 and \
               expected_wait_time + expected_request_time > request.timeout:
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
        self.__calls = 0
        now = time()
        while (self.__curr_timeblock_start + self.period < now):
            self.__curr_timeblock_start += self.period  # TODO convert seconds to timedelta
        while self.__calls < self.limit:
            try:
                (priority, request, asyncresult) = self.__requests.get(block=False)
                self.call()
                gevent.spawn(self.doRequest, request, asyncresult)
            except gevent.queue.Empty:
                break

    def doRequest(self, request, asyncresult):
        try:
            begin = time()
            http = httplib2.Http()

            if (begin - request.created) > request.timeout:
                raise TimeoutException('The request timed out while waiting in the rate limiter queue')

            body = None
            print ('### request.body: %s' % request.body)
            if request.body is not None:
                body = urllib.urlencode(request.body, True)
            response, content = http.request(request.url, request.verb, headers=request.headers, body=body)
            if response.status >= 400:
                self.fail(response, content)

            asyncresult.set((response, content))

            end = time()
            elapsed = end - begin
            realized_dur = end - request.created
            print('realized dur: %s  expected dur: %s' % (realized_dur, request.log.expected_dur))

            self._addDurationLog(elapsed)

            return response, content
        except Exception as e:
            print('Exception in doRequest: %s' % ''.join(traceback.format_exc()))
            asyncresult.set_exception(e)
            raise e