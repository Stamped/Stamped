#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils, logs, gearman, pickle

from errors import *


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
            logs.warning("Connection error: %s" % e)
            raise StampedTasksConnectionError()

        except gearman.ServerUnavailable as e:
            logs.warning("Server unavailable: %s" % e)
            raise StampedTasksServerUnavailable()

        except Exception as e:
            logs.warning("An error occurred connecting to gearman: %s (%s)" % (type(e), e))
            raise 

    return __client

def call(job, payload, **options):
    # Naming convention is "namespace::function"
    assert '::' in job

    # Run synchronously if not on EC2
    if not utils.is_ec2():
        logs.warning("Local - Running synchronously")
        raise Exception

    # Connect to broker
    client = getClient()

    # Submit job
    client.submit_job(job, pickle.dumps(payload), background=True)

    return True
