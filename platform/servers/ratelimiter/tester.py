#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import gevent
from gevent     import monkey
monkey.patch_all()
from gevent.pool import Pool

import rpyc
from optparse   import OptionParser
from time       import sleep

def parseCommandLine():
    usage   = "Usage: %prog [options] command [args]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)

    parser.add_option("-H", "--host", default="localhost", type="string",
        action="store", dest="host", help="host address")

    parser.add_option("-p", "--port", default=18861, type="int",
        action="store", dest="port", help="host port")

    parser.add_option("-s", "--service", default=None, type="string",
        action="store", dest="service", help="service name, ie 'facebook', 'twitter', 'netflix', etc")

    parser.add_option("-m", "--method", default='GET', type="string",
        action="store", dest="method", help="http verb, ie 'GET', 'POST', etc'")

    parser.add_option("-u", "--url", default=None, type="string",
        action="store", dest="url", help="url path to connect to'")

    parser.add_option("-t", "--timeout", default=5, type="int",
        action="store", dest="timeout", help="timeout for each request in seconds'")

    parser.add_option("-P", "--priority", default='high', type="string",
        action="store", dest="priority", help="priority of request as int. lower is higher priority'")

    parser.add_option("-n", "--num_requests", default=1, type="int",
        action="store", dest="num_requests", help="number of requests to run simultaneously'")

    (options, args) = parser.parse_args()

    return options

import random

def makeRequest(host, port, service, priority, timeout, method, url):
    sleep(random.random()*3)
    if timeout == 0:
        timeout = None
    print('requesting... service: %s  priority: %s  timeout: %s  method: %s  url: %s' % (service, priority, timeout, method, url))
    conn = rpyc.connect(host, port)
    response, content = conn.root.request(service, priority, timeout, method, url)
    print('finished request.')

def main():
    # parse

    options     = parseCommandLine()
    options     = options.__dict__

    host        = options.pop('host', 'localhost')
    port        = options.pop('port', 18861)
    service     = options.pop('service', None)
    url         = options.pop('url', None)
    method      = options.pop('method', 'GET')
    timeout     = options.pop('timeout', 5)
    priority    = options.pop('priority', 0)
    num_requests = options.pop('num_requests', 1)

    if service is None or url is None:
        print ('missing required options')
        return

    #pool    = Pool(num_requests)
    #for i in range(num_requests):
    #    pool.spawn(makeRequest, None, service, priority, timeout, method, url)
    #pool.join()
    threads = [gevent.spawn(makeRequest, host, port, service, priority, timeout, method, url) for i in xrange(num_requests)]
    print ('finished thread creation')
    gevent.joinall(threads)

if __name__ == '__main__':
    main()