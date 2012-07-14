#!/usr/bin/env python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = ['RateLimiter','RateException']

import Globals
from logs   import report
try:
    from time           import time
    from threading      import Lock
    from gevent         import sleep
    from gevent.pool    import Pool
    from gevent.coros   import Semaphore
    import logs
    from sys            import argv
except:
    report()
    raise

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

class RateException(Exception):
    pass

class RateLimiter(object):

    def __init__(self, cps=None, cpm=None, cph=None, cpd=None, max_wait=None):
        self.__max_wait = max_wait
        self.__limits = {}

        if cps is not None and cps != 0:
            self.__limits['calls per second'] = RateLimit(cps, 1)

        if cpm is not None and cpm != 0:
            self.__limits['calls per minute'] = RateLimit(cpm, 60)

        if cph is not None and cph != 0:
            self.__limits['calls per hour'] = RateLimit(cph, 60*60)

        if cpd is not None and cpd != 0:
            self.__limits['calls per day'] = RateLimit(cpd, 60*60*24)

        self.__semaphore = Semaphore()

    def __enter__(self):
        begin  = time()
        locked = self.__semaphore.acquire(timeout=self.__max_wait)

        if locked:
            try:
                max_wait = 0
                max_name = None
                now      = time()

                for name, limit in self.__limits.items():
                    wait = limit.wait(now)

                    if wait > max_wait:
                        max_name = name
                        max_wait = wait

                if self.__max_wait is not None and max_wait > self.__max_wait:
                    raise RateException('Rate limit exceeded for %s' % max_name)

                if max_wait > 0:
                    end = now + max_wait

                    while True:
                        cur = time()
                        if cur >= end:
                            break
                        else:
                            sleep( end - cur)

                for name, limit in self.__limits.items():
                    wait = limit.wait()
                    if wait > 0:
                        logs.warning('%s wait should be 0 is %s' % (name, wait))

                    limit.call()
            finally:
                self.__semaphore.release()
        else:
            raise RateException('Max wait (%s) exceeded trying to get slot' % self.__max_wait)

    def __exit__(self, exctype, value, trace):
        return False

if __name__ == '__main__':
    rate        = 1
    name        = 'cps'
    count       = 10
    max_wait    = 2

    if len(argv) > 1:
        rate = float(argv[1])

    if len(argv) > 2:
        name = argv[2]

    if len(argv) > 3:
        count = int(argv[3])

    if len(argv) > 4:
        max_wait = float(argv[4])

    kwargs  = {name:rate,'max_wait':max_wait}
    limiter = RateLimiter(**kwargs)

    def test(value):
        try:
            with limiter:
                print(value)
        except RateException as e:
            print('Caught RateException: %s' % e.message)

    pool = Pool(100)

    for i in range(count):
        pool.spawn(test, i)

    pool.join()
    print("Completed")

