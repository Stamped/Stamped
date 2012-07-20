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
from servers.ratelimiter.RateLimiterService import StampedRateLimiterService
import libs.ec2_utils
from collections                import deque


FAIL_LIMIT = 10
FAIL_PERIOD = 60*3
BLACKOUT_WAIT = 60*5
EMAIL_WAIT = 60*5
DEFAULT_TIMEOUT = 3
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
        self.__stack_name = stack_info.instance.stack
        self.__node_name = stack_info.instance.name
        self.__last_email_time = None
        self.__emails = deque()

        # determine the private ip address of the ratelimiter instance for this stack
        ratelimiter_nodes = libs.ec2_utils.get_nodes('ratelimiter')
        if ratelimiter_nodes is None or len(ratelimiter_nodes) != 1:
            logs.error("Could not find a node with tag 'ratelimiter' on same stack")
            self.__host = 'localhost'
        else:
            self.__host = ratelimiter_nodes[0]['private_ip_address']
        self.__port = 18861

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

    def sendFailLogEmail(self):
        if len(self.__fails) == 0:
            return

        output = '<html>'
        output += "<h3>RateLimiter RPC Server Failure</h3>"
        output += "<p>On stack '%s' instance '%s'.</p>" % (self.__stack_name, self.__node_name)
        output += "<p><i>There were %s failed requests to the rpc server within the last %s seconds</i></p>" %\
                  (self.__fail_limit, self.__fail_period)
        back_online = time.strftime('%m/%d/%Y %H:%M:%S', time.localtime(self.__blackout_start + self.__blackout_wait)) # Timestamp
        output += "<p>Waiting for %s seconds.  Will use local Rate Limiter service in until: %s</p>" % (self.__blackout_wait, back_online)

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
            email['subject'] = "RateLimiter RPC server failure"
            email['body'] = output
            utils.sendEmail(email, format='html')
        except Exception as e:
            print('UNABLE TO SEND EMAIL: %s' % e)

        return output

    def _fail(self, exception):
        if self.__blackout_start is not None:
            return

        self.__fails.append(self.FailLog(exception))

        now = time.time()

        cutoff = now - self.__fail_period
        count = 0

        while len(self.__fails) > 0:
            if self.__fails[0].timestamp > cutoff:
                self.__fails.popleft()
            else:
               break

        count = len(self.__fails)

        if count >= self.__fail_limit:
            self.__blackout_start = time.time()
            self.__local_rlservice.loadDbLog()    # update the local call log from the db

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
            return False

    def _rpc_service_request(self, host, port, service, method, url, body, header, priority, timeout):
        conn = rpyc.connect(host, port)

        async_request = rpyc.async(conn.root.request)
        try:
            asyncresult = async_request(service, priority, timeout, method, url, pickle.dumps(body), pickle.dumps(header))
            asyncresult.set_expiry(timeout)
            response, content = asyncresult.value
        except RateException as e:
            logs.info('RateException occurred during third party request: %s' % e)
            raise e
        except Exception as e:
            logs.error('RPC service request fail: %s' % e)
            raise StampedThirdPartyRequestFailError("There was an error fulfilling a third party http request")

        return pickle.loads(response), content

    def _local_service_request(self, service, method, url, body, header, priority, timeout):
        response, content = self._local_rlservice.handleRequest(service, priority, timeout, method, url, body, header)
        return response, content

    def request(self, service, method, url, body, header, priority, timeout):
        print('### is_ec2: %s' % self.__is_ec2)
        sleep(0)
        if not self.__is_ec2 or self._isBlackout():
            return self._local_service_request(service, method.upper(), url, body, header, priority, timeout)
        try:
            print('### attempting rpc service request')
            return self._rpc_service_request(self.__host, self.__port, service, method.upper(), url, body, header, priority, timeout)
        except Exception as e:
            print('### failed while attempting rpc service request: %s' % e)
            self._fail(e)
            return self._local_service_request(service, method.upper(), url, body, header, priority, timeout)


__rl_state = None
def rl_state():
    global __rl_state
    if __rl_state is not None:
        return __rl_state

    __rl_state = RateLimiterState(FAIL_LIMIT, FAIL_PERIOD, BLACKOUT_WAIT)
    return __rl_state


def service_request(service, method, url, body={}, header={}, query_params = {}, priority='low', timeout=DEFAULT_TIMEOUT):
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

    response, content = rl_state().request(service, method, url, body, header, priority, timeout)

    if response.status > 400:
        logs.warning('service request returned an error response.  status code: %s  content: %s' % (response.status, content))

    return response, content