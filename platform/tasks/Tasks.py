#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils
import gearman, pickle

from errors import *

"""
StampedAPI calls invoke(name, kwargs=kwargs)
This is intercepted and we check to see if the broker is available
If broker is unavailable:
    - Retry N times
    - Fall back to running locally (if specified)
If broker is available:
    - Serialize payload
    - pass payload to broker
    - return
"""

class StampedTasksConnectionError(Exception):
    pass

class StampedTasksServerUnavailable(Exception):
    pass



__client = None

def getClient():
    global __client 

    if __client is None:
        try:
            __client = gearman.GearmanClient(['localhost:4730'])
        
        except gearman.ConnectionError as e:
            print 'CONNECTION ERROR: %s' % e
            raise StampedTasksConnectionError()

        except gearman.ServerUnavailable as e:
            print 'SERVER UNAVAILABLE: %s' % e 
            raise StampedTasksServerUnavailable()

        except Exception as e:
            print 'FAILED: %s' % e
            raise 

    return __client

def call(job, payload, **options):

    # Run synchronously if not on EC2
    # if not utils.is_ec2():
    #     raise Exception

    # Connect to broker
    client = getClient()

    # Parse options
    background = options.pop('background', True)

    # Submit job
    client.submit_job(job, pickle.dumps(payload), background=background)

    return True


def callFunction(fn, payload, **options):
    try:
        return tasks.Tasks.call(fn.__name__, payload)
    except Exception as e:
        logs.warning()
        fallback = options.pop('fallback', True)
        if fallback:
            return fn(**payload)

        raise





        