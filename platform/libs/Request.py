import gevent
from gevent     import monkey
monkey.patch_all()

import logs
import utils
import rpyc
import urllib
from time                       import time, sleep
from servers.ratelimiter.server import StampedRateLimiterService


RL_HOST = 'localhost'
RL_PORT = 18861

request_fails = 0
fail_threshold = 200
fail_start = None
fail_wait = 60*5

local_rlservice = None

def _isRpcServiceAvailable():
    pass

def _fail():
    global request_fails, fail_start

    if fail_start is not None:
        return

    request_fails += 1
    if request_fails >= fail_threshold:
        fail_start = time()

def _isFailed():
    global request_fails, fail_start

    if fail_start is None:
        return False
    if fail_start + fail_wait > time():
        return True
    else:
        fail_start = None
        request_fails = 0
        return False


def _rpc_service_request(host, port, service, method, url, body={}, header={}, priority='high', timeout=5):
    global request_fails

    conn = rpyc.connect(host, port)

    async_request = rpyc.async(conn.root.request)
    try:
        asyncresult = async_request(service, priority, timeout, method, url)
        asyncresult.set_expiry(timeout)
        response, content = asyncresult.value
    except RateException as e:
        logs.info('RateException occurred during third party request: %s' % e)
        return
    except Exception as e:
        request_fails += 1
        logs.error('RPC service request fail: %s' % e)
        if frequest_fails >= fail_threshold:
            logs.error('RPC service FAIL THRESHOLD REACHED')
        raise StampedThirdPartyRequestFailError("There was an error fulfilling a third party http request")
    return response, content

def _local_service_request(service, method, url, body={}, header={}, priority='high', timeout=5):
    response, content = local_rlservice.exposed_request(service, priority, timeout, method, url, body, header)
    return response, content



def service_request(service, method, url, body={}, header={}, query_params = {}, priority='high', timeout=5):
    global local_rlservice, request_fails

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

    if local_rlservice is None:
        if utils.is_ec2():
            local_rlservice = StampedRateLimiterService(RL_PORT, throttle=True)
        else:
            local_rlservice = StampedRateLimiterService(RL_PORT, throttle=True)

    if not utils.is_ec2() or _isFailed():
        return _local_service_request(service, method.upper(), url, body, header, priority, timeout)
    try:
        return _rpc_service_request(RL_HOST, RL_PORT, service, method.upper(), url, body, header, priority, timeout)
    except:
        request_fails += 1
        return _local_service_request(service, method.upper(), url, body, header, priority, timeout)
