#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from gevent     import monkey
monkey.patch_all()
from gevent.coros import Semaphore

import logs
import utils
import rpyc
import urllib
import pickle
import time
from errors import *
from servers.ratelimiter.RateLimiterService import StampedRateLimiterService
from servers.ratelimiter.RateLimiter2 import DailyLimitException, WaitTooLongException, TimeoutException, TooManyFailedRequestsException
import libs.ec2_utils
from collections import deque

FAIL_LIMIT = 10
FAIL_PERIOD = 60*3
BLACKOUT_WAIT = 60*5
EMAIL_WAIT = 60*5
DEFAULT_TIMEOUT = 5
RL_HOST = 'localhost'
RL_PORT = 18861


class RateLimiterState(object):
    def __init__(self, fail_limit, fail_period, blackout_wait):
        self.__local_rlservice = None
        self.__request_fails = 0
        self.__fails = deque()
        self.__fail_limit = fail_limit
        self.__fail_period = fail_period
        self.__blackout_start = None
        self.__blackout_wait = blackout_wait
        self.__is_ec2 = utils.is_ec2()
        self.__service_init_semaphore = Semaphore()
        stack_info = libs.ec2_utils.get_stack()
        self.__stack_name = 'localhost'
        self.__node_name = 'localhost'
        if stack_info is not None:
            self.__stack_name = stack_info.instance.stack
            self.__node_name = stack_info.instance.name
        self.__last_email_time = 0
        self.__emails = deque()

        # determine the private ip address of the ratelimiter instance for this stack
        self._getHost()
        print('### host: %s' % self.__host)

    class FailLog(object):
        def __init__(self, exception):
            self.timestamp = time.time()
            self.exception = exception

    @property
    def _local_rlservice(self):
        if self.__local_rlservice is None:
            # use a semaphore here because if two requests come in immediately, we might instantiate two services
            self.__service_init_semaphore.acquire()
            if self.__local_rlservice is None:
                if self.__is_ec2:
                    self.__local_rlservice = StampedRateLimiterService(throttle=True)
                else:
                    self.__local_rlservice = StampedRateLimiterService(throttle=False)
            self.__service_init_semaphore.release()

        return self.__local_rlservice

    def _getHost(self):
        ratelimiter_nodes = None
        try:
            ratelimiter_nodes = libs.ec2_utils.get_nodes('ratelimiter')
        except:
            logs.error("Could not find a node with tag 'ratelimiter on same stack")
        if ratelimiter_nodes is None:
            self.__host = 'localhost'
        else:
            self.__host = ratelimiter_nodes[0]['private_ip_address']
        self.__port = 18861

    def sendFailLogEmail(self):
        if len(self.__fails) == 0:
            return

        output = '<html>'
        output += "<h3>RateLimiter RPC Server Failure on %s</h3>" % self.__stack_name
        output += "<p>On stack '%s' instance '%s'.</p>" % (self.__stack_name, self.__node_name)
        output += "<p><i>There were %s failed requests to the rpc server within the last %s seconds</i></p>" %\
                  (self.__fail_limit, self.__fail_period)
        back_online = time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(self.__blackout_start + self.__blackout_wait)) # Timestamp
        output += "<p>Waiting for %s seconds.  Will use local Rate Limiter service until: %s</p>" % (self.__blackout_wait, back_online)

        output += '<h3>Fail Log</h3>'

        output += '<table border=1 cellpadding=5>'
        output += '<tr>'
        labels = ['Timestamp', 'Exception']
        for label in labels:
            output += '<td style="font-weight:bold">%s</td>' % label
        output += '</tr>'

        for fail in self.__fails:
            output += '<tr>'
            output += '<td valign=top>%s</td>' % time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(fail.timestamp)) # Timestamp
            output += '<td valign=top>%s</td>' % fail.exception
            output += '</tr>'

        output += '</table>'

        output += '</html>'


        try:
            email = {}
            email['from'] = 'Stamped <noreply@stamped.com>'
            email['to'] = 'dev@stamped.com'
            email['subject'] = "%s RateLimiter RPC server failure" % self.__stack_name
            email['body'] = output
            utils.sendEmail(email, format='html')
        except Exception as e:
            print('UNABLE TO SEND EMAIL: %s' % e)

        return output

    def _fail(self, exception):
        try:
            del threading.local().rateLimiter
        except:
            pass

        self._getHost()
        if self.__blackout_start is not None:
            return

        self.__fails.append(self.FailLog(exception))

        now = time.time()

        cutoff = now - self.__fail_period
        count = 0

        while len(self.__fails) > 0:
            if self.__fails[0].timestamp < cutoff:
                self.__fails.popleft()
            else:
               break

        count = len(self.__fails)

        if count >= self.__fail_limit:
            print('### RPC server fail threshold reached')
            self.__blackout_start = time.time()
            #self.__local_rlservice.loadDbLog()    # update the local call log from the db


            logs.error('RPC server request FAIL THRESHOLD REACHED')
            # Email dev if a fail limit was reached
            if self.__is_ec2:
                if self.__last_email_time is not None and (time.time() - self.__last_email_time) > EMAIL_WAIT:
                    self.sendFailLogEmail()
                    self.__last_email_time = time.time()

    def _isBlackout(self):
        if self.__blackout_start is None:
            return False
        if self.__blackout_start + self.__blackout_wait > time.time():
            return True
        else:
            self.__blackout_start = None
            self.__request_fails = 0
#            self.__local_rlservice.shutdown()
#            self.__local_rlservice = None
            return False

    @property
    def _rpc_service_connection(self):
        try:
            return threading.local().rateLimiter
        except AttributeError:
            config = {
                'allow_pickle' : True,
                'allow_all_attrs' : True,
                'instantiate_custom_exceptions' : True,
                'import_custom_exceptions' : True,
                }
            threading.local().rateLimiter = rpyc.connect(host, port, config=config)
            return threading.local().rateLimiter

    def _rpc_service_request(self, host, port, service, method, url, body, header, priority, timeout):
        async_request = rpyc.async(self._rpc_service_connection.root.request)
        asyncresult = async_request(service, priority, timeout, method, url, pickle.dumps(body), pickle.dumps(header))
        asyncresult.set_expiry(timeout)
        response, content = asyncresult.value

        return pickle.loads(response), content

    def _local_service_request(self, service, method, url, body, header, priority, timeout):
        response, content = self._local_rlservice.handleRequest(service, priority, timeout, method, url, body, header)
        return response, content

    def request(self, service, method, url, body, header, priority, timeout):
        if not self.__is_ec2 or self._isBlackout():
            return self._local_service_request(service, method.upper(), url, body, header, priority, timeout)
        try:
            logs.info('### attempting rpc service request')
            return self._rpc_service_request(self.__host, self.__port, service, method.upper(), url, body, header, priority, timeout)
        except DailyLimitException as e:
            raise StampedThirdPartyRequestFailError("Hit daily rate limit for service: '%s'" % service)
        except WaitTooLongException as e:
            raise StampedThirdPartyRequestFailError("'%s' request estimated wait time longer than timeout" % service)
        except TimeoutException as e:
            raise StampedThirdPartyRequestFailError("'%s' request timed out." % service)
        except TooManyFailedRequestsException as e:
            raise StampedThirdPartyRequestFailError("%s" % e)
        except Exception as e:
            import traceback
            print('### caught exception  type: %s  e: %s' % (type(e), e))
            logs.info("RPC Service Request fail."
                        "service: %s  method: %s  url: %s  body: %s  header: %s"
                        "priority: %s  timeout: %s  Exception: %s  Stack: %s" %
                        (service, method, url, body, header, priority, timeout, e, traceback.format_exc()))
            self._fail(e)
        logs.info('### Falling back to local rate limiter request')
        return self._local_service_request(service, method.upper(), url, body, header, priority, timeout)


__rl_state = None
def rl_state():
    global __rl_state
    if __rl_state is not None:
        return __rl_state

    __rl_state = RateLimiterState(FAIL_LIMIT, FAIL_PERIOD, BLACKOUT_WAIT)
    return __rl_state


def service_request(service, method, url, body={}, header={}, query_params = {}, priority='low', timeout=DEFAULT_TIMEOUT):
    if timeout is None:
        timeout = DEFAULT_TIMEOUT
    if body is None:
        body = {}
    if header is None:
        header = {}
    if query_params is None:
        query_params = {}

    if query_params != {}:
        encoded_params  = urllib.urlencode(query_params)
        if url.find('?') == -1:
            url += "?%s" % encoded_params
        else:
            url += "&%s" % encoded_params

    logs.info('### called service_request.  service: %s  url: %s   priority: %s  timeout: %s' % (service, url, priority, timeout))

    response, content = rl_state().request(service, method, url, body, header, priority, timeout)

    if response.status > 400:
        logs.warning('service request returned an error response.  status code: %s  content: %s' % (response.status, content))

    return response, content