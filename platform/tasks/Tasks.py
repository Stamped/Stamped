#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils, logs, gearman, pickle, time
import libs.ec2_utils

from errors import *
from datetime import datetime, timedelta
from bson.objectid import ObjectId


# Global client
__client = None

# Global list of errors
__errors = [] 

# Global timestamp for cooldown period
__cooldown = None 


def getHosts():
    stack = libs.ec2_utils.get_stack()

    if stack is None:
        return ['localhost:4730']

    hosts = []
    for node in stack['nodes']:
        if 'broker' in node['roles'] or 'monitor' in node['roles']: # TEMP: monitor is deprecated
            hosts.append("%s:4730" % node['private_ip_address'])

    assert len(hosts) > 0

    return hosts

def getClient():
    global __client 

    if __client is None:
        try:
            hosts = getHosts()
            __client = gearman.GearmanClient(hosts)
        
        except gearman.errors.ConnectionError as e:
            logs.warning("Connection error: %s" % e)
            raise StampedTasksConnectionError()

        except gearman.errors.ServerUnavailable as e:
            logs.warning("Server unavailable: %s" % e)
            raise StampedTasksServerUnavailable()

        except Exception as e:
            logs.warning("An error occurred connecting to gearman: %s (%s)" % (type(e), e))
            raise 

    return __client

def resetClient():
    global __client
    __client = None

def call(queue, key, payload, **options):
    # Naming convention is "namespace::function"
    # assert '::' in key

    # Run synchronously if not on EC2
    # if not utils.is_ec2():
    #     logs.warning("Local - Running synchronously")
    #     raise Exception

    global __errors
    global __cooldown

    maxErrors = 5
    numErrors = len(__errors)

    # Initiate cooldown period if number of errors is too high
    if numErrors > maxErrors:
        msg = "Number of errors (%s) exceeds maximum (%s): cooling down" % (numErrors, maxErrors)
        logs.warning(msg)
        __cooldown = datetime.utcnow()
        __errors = []

    # Fail if in cooldown period
    if __cooldown is not None and datetime.utcnow() - timedelta(minutes=5) < __cooldown:
        msg = "Cooling down until %s" % __cooldown
        logs.warning(msg)
        raise Exception(msg)

    # Build payload
    data = {
        'task_id': str(ObjectId()),
        'key': key,
        'data': payload,
        'timestamp': datetime.utcnow()
    }

    maxRetries = 5
    numRetries = 0

    while True:
        try:
            # Submit job
            logs.info("Submitting task: %s" % data)
            client = getClient()
            client.submit_job(queue, pickle.dumps(data), background=True)

            # Reset errors
            __errors = []
            __cooldown = None

            return True 

        except Exception as e:
            # Retry
            numRetries += 1
            if numRetries <= maxRetries:
                time.sleep(0.1)
                continue

            logs.warning("Task failed: %s (%s)" % (type(e), e))

            # Reset client
            resetClient()

            # Cap the number of errors logged
            __errors.append(e)
            __errors = __errors[-25:]
            numErrors = len(__errors)

            # Initiate a cool down period
            if numErrors >= maxErrors:
                __cooldown = datetime.utcnow()

            # Send an email alert the first time this happens
            if numErrors == maxErrors:
                msg = "Unable to connect to task broker: %s" % getHosts()
                logs.warning(msg)

                if utils.is_ec2():
                    # Send email
                    email = {}
                    try:
                        stack_info = libs.ec2_utils.get_stack()
                        email['subject'] = "%s.%s - Unable to connect to task broker" % \
                            (stack_info.instance.stack, stack_info.instance.name)
                    except Exception:
                        subject = msg

                    email['body'] = "All async tasks running locally\n\n%s\n\n" % msg
                    for error in __errors:
                        email['body'] += str(error)
                        email['body'] += '\n'

                    email['from'] = 'Stamped <noreply@stamped.com>'
                    email['to'] = 'dev@stamped.com'

                    utils.sendEmail(email)

            raise 
    
