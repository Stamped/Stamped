#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

# For core gearman functionality
import gearman, gevent, pickle
import libs.ec2_utils

# For signal handling
import signal, os

# For logging
from datetime import datetime
import logs
import utils
import traceback

# For arg handling
import sys

def _api():
    from MongoStampedAPI import globalMongoStampedAPI
    return globalMongoStampedAPI()

def _warningEmail(subject):
    if libs.ec2_utils.is_ec2():
        try:
            email = {}
            email['from'] = 'Stamped <noreply@stamped.com>'
            email['to'] = 'dev@stamped.com'
            email['subject'] = subject
            email['body'] = logs.getHtmlFormattedLog()
            utils.sendEmail(email, format='html')
        except Exception as e:
            logs.warning('UNABLE TO SEND EMAIL: %s' % (e,))
    
class StampedWorker(gearman.GearmanWorker):
    """
    Minimal wrapper for after_poll callback for signal based shutdown
    """

    killed = False # class level flag for 

    def __init__(self, host):
        gearman.GearmanWorker.__init__(self, host)
        self.__terminated = False

    def after_poll(self, any_activity):
        return not self.__terminated

    def signalHandler(self, signum, frame):
        """
        Signal handler for terminate.
        """
        if signum == 15:
            self.__terminated = True
        else:
            message = 'unhandled signal: %s\n%s' % (signum, ''.join(traceback.format_stack()))
            logs.warning(message)
            _warningEmail('Worker terminated with SIGQUIT')
            sys.exit(1)

def getHosts():
    """
    Retrieve the list of Gearman servers.

    TODO - not audited
    TODO - not tested
    """
    stack = libs.ec2_utils.get_stack()

    if stack is None:
        return ['localhost:4730']

    hosts = []
    for node in stack['nodes']:
        if 'broker' in node['roles'] or 'monitor' in node['roles']: # TEMP: monitor is deprecated
            hosts.append("%s:4730" % node['private_ip_address'])

    assert len(hosts) > 0

    return hosts

def pickleDecoder(data):
    job_data = pickle.loads(data)
    key = job_data.pop('key', None)
    task_id = job_data.pop('task_id', None)
    data = job_data.pop('data', None)
    return task_id, key, data, job_data 

def enterWorkLoop(queue, handler, decoder=pickleDecoder):
    worker = StampedWorker(getHosts())
    signal.signal(signal.SIGTERM, worker.signalHandler)
    signal.signal(3, worker.signalHandler)
    def wrapper(worker, job):
        try:
            task_id, key, data, extra = pickleDecoder(job.data)
            handler(task_id, key, data, **extra)
        except Exception as e:
            basic_message = "Invalid job: %s %s" % (job.task, job.unique)
            logs.error(basic_message)
            logs.report()
            _warningEmail(basic_message)
        return ''
    worker.register_task(queue, wrapper)
    worker.work(poll_timeout=1)
    logs.info('Terminating worker')

def loggingHandler(handler):
    api = _api()
    def wrapper(task_id, key, data, **kwargs):
        try:
            logs.begin(saveLog=api._logsDB.saveLog,
                       saveStat=api._statsDB.addStat,
                       nodeName=api.node_name)
            logs.async_request(key)
            logs.info("Request %s: %s: %s: %s" % (task_id, key, data, kwargs))
            handler(task_id, key, data, **kwargs)
            logs.info("Finished with request %s" % (task_id,))
        except Exception as e:
            logs.error("Failed request %s" % (task_id,))
            logs.report()
            _warningEmail('%s - %s failed (%s)' % (api.node_name, key, datetime.utcnow().isoformat()))
        finally:
            logs.info('Saving request log for request %s' % (task_id,))
            try:
                logs.save()
            except Exception:
                print 'Unable to save logs'
                import traceback
                traceback.print_exc()
                logs.warning(traceback.format_exc())
    return wrapper

def pushToUnhandledQueue(task_id, key, data, **kwargs):
    """
    TODO put things on unhandled queue
    """
    from tasks.Tasks import call
    call('error', key, data)

def attributeHandler(target, fallbackHandler=pushToUnhandledQueue):
    def wrapper(task_id, key, data, **kwargs):
        comps = key.split('::')
        if len(comps) == 2:
            k = comps[1]
            if hasattr(target, k):
                v = getattr(target, k)
                v(**data)
                return
        if fallbackHandler is not None:
            fallbackHandler(task_id, key, data, **kwargs)
        else:
            logs.warning('Dropped task! %s %s', task_id, key)
    return wrapper

###########################################

def apiHandler():
    from MongoStampedAPI import globalMongoStampedAPI
    api = globalMongoStampedAPI()
    return loggingHandler(attributeHandler(api))

def enrichHandler():
    from MongoStampedAPI import globalMongoStampedAPI
    api = globalMongoStampedAPI()
    return loggingHandler(attributeHandler(api))

def printer(task_id, key, data, **kwargs):
    from pprint import pformat
    logs.warning('Error task: %s, %s\n%s' % (task_id, key, pformat(data)))

def errorHandler():
    return loggingHandler(printer)

###########################################

if __name__ == '__main__':
    from MongoStampedAPI import globalMongoStampedAPI
    if len(sys.argv) != 2:
        sys
        print "Usage - python Worker.py (enrich | api)"
        sys.exit(1)
    queue = sys.argv[1]
    handler = None
    if queue == 'enrich':
        handler = enrichHandler()
    elif queue == 'api':
        handler = apiHandler()
    elif queue == 'error':
        handler = errorHandler()

    if handler is not None:
        enterWorkLoop(queue, handler)
    else:
        print "Unrecognized queue: %s" % queue


