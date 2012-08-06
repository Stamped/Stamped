#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import datetime
import logs
import pprint
import time
from api.MongoStampedAPI import MongoStampedAPI, globalMongoStampedAPI

TIME_IMMEMORIAL = datetime.datetime(1970, 1, 1)

class PeriodicTaskRunner(object):
    def __init__(self):
        self.__registered_tasks = []
        self.__api = globalMongoStampedAPI()

    def register_task(self, interval, *args, **kwargs):
        """
        Registers a task to be invoked periodically.

        All but the first positional argument is passed directy to the `callTask` function of
        StampedAPI, which in turn enqueues the task to the work queue. The result of computation is
        always discarded.

        Note that the "fallback" option will always be False.

        Args:
            interval: a timedelta object denoting the interval between task invocations
            args and kwargs: arguments that are passed down directly to `callTask`. NB: these
                             arguments are reused for every invocation.
        """
        kwargs['fallback'] = False
        self.__registered_tasks.append((interval, args, kwargs, TIME_IMMEMORIAL))

    def run(self):
        """
        The infinite loop that invokes tasks based on pre-set time intervals.
        """
        formatted_tasks = pprint.pformat(self.__registered_tasks)
        logs.info('Starting periodic tasks runner with tasks ' + formatted_tasks)

        while True:
            sleep_time = datetime.timedelta(seconds=3600)
            now = datetime.datetime.now()

            updated_tasks = []
            for interval, args, kwargs, last_run in self.__registered_tasks:
                if now - last_run >= interval:
                    logs.info('Invoking task: ' + pprint.pformat((args, kwargs)))
                    try:
                        self.__api.callTask(*args, **kwargs)
                    except Exception:
                        pass
                    logs.info('Next invocation: ' + str(now + interval))
                    last_run = now
                sleep_time = min(interval - (now - last_run), sleep_time)
                updated_tasks.append((interval, args, kwargs, last_run))
            self.__registered_tasks = updated_tasks

            sleep_seconds = max(int(sleep_time.total_seconds()), 5)
            logs.info('Sleeping for %d seconds' % sleep_seconds)
            time.sleep(sleep_seconds)

if __name__ == '__main__':
    task_runner = PeriodicTaskRunner()
    task_runner.register_task(
            datetime.timedelta(hours=3),
            MongoStampedAPI.crawlExternalSourcesAsync, {})
    task_runner.register_task(
            datetime.timedelta(days=1),
            MongoStampedAPI.updateAutoCompleteIndexAsync, {})
    task_runner.run()
