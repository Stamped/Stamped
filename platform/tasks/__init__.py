#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import APITasks

import atexit, logs, pprint, time, utils

from datetime           import datetime, timedelta
from celery.task        import task
from celery.task.base   import BaseTask
from utils              import LoggingThreadPool

__broker_status__   = utils.AttributeDict({
    'errors'  : [], 
    'time'    : None, 
    'handler' : None, 
})

local_worker_pool = None

def invoke(task, args=None, kwargs=None, **options):
    """
        Main entrypoint to invoke asynchronous Celery tasks, with custom logic 
        to fallback to local, synchronous execution in the event that we run 
        into problems contacting the Celery task broker.
    """
    
    #msg = "INVOKE: %s" % task
    #logs.debug(msg)

    if not utils.is_ec2():
        global local_worker_pool
        if local_worker_pool is None:
            local_worker_pool = LoggingThreadPool(16)
            atexit.register(local_worker_pool.join)
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        return local_worker_pool.spawn(task.run, *args, **kwargs)

    assert isinstance(task, BaseTask)
    global __broker_status__
    
    max_retries = 5
    max_errors  = 5
    num_errors  = len(__broker_status__.errors)
    
    attempt_async = num_errors < max_errors or \
                    (__broker_status__.time is not None and \
                     datetime.utcnow() - timedelta(minutes=5) >= __broker_status__.time)

    if attempt_async:
        error   = None
        retries = 0
        
        while True:
            try:
                retval = task.apply_async(args, kwargs, **options)

                # clear built-up errors now that we've successfully reestablished 
                # our connection with the message broker
                __broker_status__['errors'] = []
                
                return retval
            except TypeError, e:
                logs.warn("invalid async call (%s); args=%s; kwargs=%s" % (e, args, kwargs))
                error = e
                break
            except Exception, e:
                retries += 1
                
                if retries > max_retries:
                    error = e
                    break

                time.sleep(0.1)

        if error is not None:
            logs.warn("async failed: (%s) %s" % (type(error), error))
            
            if num_errors < max_errors * 5:
                __broker_status__.errors.append(error)
                num_errors = len(__broker_status__.errors)
            
            if num_errors >= max_errors:
                __broker_status__.time = datetime.utcnow()
                
                if num_errors == max_errors:
                    import celeryconfig
                    
                    msg = "Error: API unable to contact Celery's asnc task broker: %s" % celeryconfig.BROKER_URL
                    logs.warn(msg)
                    utils.log(msg)
                    
                    if utils.is_ec2():
                        if __broker_status__.handler is None:
                            from libs.notify import StampedNotificationHandler
                            __broker_status__.handler = StampedNotificationHandler()
                        
                        handler = __broker_status__.handler
                        subject = msg
                        body    = "All async tasks will temporarily be run synchronously / locally.\n\n"
                        
                        for error in __broker_status__.errors:
                            body += str(error)
                            body += "\n"
                        
                        import libs.ec2_utils
                        body += "\n" + pprint.pformat(dict(libs.ec2_utils.get_stack())) + "\n"
                        
                        handler.email(subject, body)
    
    # broker is not responding so attempt to invoke the task synchronously / locally
    logs.warn("running async task locally '%s'" % task)
    return task.apply(args, kwargs, **options)

