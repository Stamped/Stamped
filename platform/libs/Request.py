import gevent
from gevent     import monkey
monkey.patch_all()

import logs
import utils
import rpyc
import urllib
from time                       import time, sleep
from servers.ratelimiter.server import StampedRateLimiterService


FAIL_LIMIT = 10
FAIL_WAIT = 60*5
RL_HOST = 'localhost'
RL_PORT = 18861


class RateLimiterState(object):
    def __init__(self, fail_limit, fail_wait, host, port):
        self.__local_rlservice = None
        self.__host = host
        self.__port = port
        self.__request_fails = 0
        self.__fail_limit = fail_limit
        self.__fail_start = None
        self.__fail_wait = fail_wait
        self.__is_ec2 = utils.is_ec2()

    @property
    def _local_rlservice(self):
        if self.__local_rlservice is None:
            if self.__is_ec2:
                self.__local_rlservice = StampedRateLimiterService(throttle=True)
            else:
                self.__local_rlservice = StampedRateLimiterService(throttle=False)

        return self.__local_rlservice

    def _fail(self):
        if self.__fail_start is not None:
            return

        self.__request_fails += 1
        if self.__request_fails >= self.__fail_threshold:
            self.__fail_start = time()
            logs.error('RPC service FAIL THRESHOLD REACHED')

    def _isFailed(self):
        if self.__fail_start is None:
            return False
        if self.__fail_start + self.__fail_wait > time():
            return True
        else:
            self.__fail_start = None
            self.__request_fails = 0
            return False

    def _rpc_service_request(self, host, port, service, method, url, body={}, header={}, priority='low', timeout=5):
        conn = rpyc.connect(host, port)

        async_request = rpyc.async(conn.root.request)
        try:
            asyncresult = async_request(service, priority, timeout, method, url)
            asyncresult.set_expiry(timeout)
            response, content = asyncresult.value
        except RateException as e:
            logs.info('RateException occurred during third party request: %s' % e)
            raise e
        except Exception as e:
            logs.error('RPC service request fail: %s' % e)
            raise StampedThirdPartyRequestFailError("There was an error fulfilling a third party http request")
        return response, content

    def _local_service_request(self, service, method, url, body={}, header={}, priority='low', timeout=5):
        response, content = self._local_rlservice.handleRequest(service, priority, timeout, method, url, body, header)
        return response, content

    def request(self, service, method, url, body={}, header={}, priority='low', timeout=5):
        if not self.__is_ec2 or self._isFailed():
            return self._local_service_request(service, method.upper(), url, body, header, priority, timeout)
        try:
            return self._rpc_service_request(self.__host, self.__port, service, method.upper(), url, body, header, priority, timeout)
        except:
            self._fail()
            return self._local_service_request(service, method.upper(), url, body, header, priority, timeout)

__rl_state = None
def rl_state():
    global __rl_state
    if __rl_state is not None:
        return __rl_state
    __rl_state = RateLimiterState(FAIL_LIMIT, FAIL_WAIT, RL_HOST, RL_PORT)
    return __rl_state

def service_request(service, method, url, body={}, header={}, query_params = {}, priority='high', timeout=5):
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