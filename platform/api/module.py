#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

import logs
import tasks.Tasks

class APIModule(object):

    def __init__(self):
        pass

    def task_key(self, queue, fn):
        return '%s::%s' % (queue, fn.__name__)

    def call_task(self, fn, payload, **options):
        try:
            queue = options.pop('queue', 'api').lower()
            key = self.task_key(queue, fn)
            return tasks.Tasks.call(queue, key, payload)

        except Exception as e:
            logs.warning("Failed to run task '%s': %s" % (fn.__name__, e))

            if options.pop('fallback', True):
                logs.info("Running locally")
                return fn(**payload)

            raise
    