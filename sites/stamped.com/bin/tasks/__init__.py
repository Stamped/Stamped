
import Globals
import APITasks

import logs, pprint, time, utils

from datetime           import datetime, timedelta
from celery.task        import task
from celery.task.base   import BaseTask

__broker_status__   = utils.AttributeDict({
    'errors'  : [], 
    'time'    : None, 
    'handler' : None, 
})

def invoke(task, args=None, kwargs=None, **options):
    """
        Main entrypoint to invoke asynchronous Celery tasks, with custom logic 
        to fallback to local, synchronous execution in the event that we run 
        into problems contacting the Celery task broker.
    """
    
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
            except Exception, e:
                retries += 1
                
                if retries > max_errors:
                    error = e
                    break
                
                time.sleep(0.01)
        
        if error is not None:
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
    return task.apply(args, kwargs, **options)

