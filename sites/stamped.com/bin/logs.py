#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import datetime, logging, os, threading, hashlib, random, time
import sys, traceback, string
import inspect, pprint

# Log
log = logging.getLogger('stamped')
log.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%H:%M:%S')

# Stream handler
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)

# File handler
log_file = "/stamped/logs/wsgi.log"
if os.path.exists(os.path.dirname(log_file)):
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

# Add handler
log.addHandler(stream_handler)

def _generateLogId():
    m = hashlib.md5(str(time.time()))
    m.update(str(random.random()))
    return str(m.hexdigest())

def _begin():
    try:
        localData.logId
    except:
        refresh()

def _log(level, msg, *args, **kwargs):
    _begin()

    try:
        fnc = inspect.stack()[2][3]
    except:
        fnc = "UNKNOWN FUNCTION"
    
    if localData.format == 'object':
        item = (datetime.datetime.utcnow(), level, fnc, msg)
        localData.log['log'].append(item)

    # else:
    msg = "%s | %-25s | %s" % (localData.logId[:6], fnc, msg)
    if level == 'warning':
        log.warning(msg, *args, **kwargs)
    elif level == 'info':
        log.info(msg, *args, **kwargs)
    else:
        log.debug(msg, *args, **kwargs)


def refresh(format=None):
    localData.logId = _generateLogId()
    localData.format = format
    localData.log = {
        'log': [],
        'begin': datetime.datetime.utcnow(),
        'request_id': localData.logId,
    }
    localData.output = None

localData = threading.local()
refresh()

def formatMessage(msg, fnc):
    msg = "%s | %-25s | %s" % (localData.logId, fnc, msg)
    return msg

# Logging Functions
def debug(msg, *args, **kwargs):
    _log('debug', msg, *args, **kwargs)

def info(msg, *args, **kwargs):
    _log('info', msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    _log('warning', msg, *args, **kwargs)

# Alternate
def warn(msg, *args, **kwargs):
    _log('warning', msg, *args, **kwargs)


# HTTP Log Requests
def begin(output=None):
    refresh(format='object')
    localData.output = output

def request(request):
    try:
        localData.log['path'] = request.path
        localData.log['method'] = request.method
        localData.log['headers'] = str(request.META)
    except:
        localData.log['request'] = 'FAIL'

def token(token):
    try:
        localData.log['token'] = token
    except:
        localData.log['token'] = 'FAIL'

def client(client_id):
    try:
        localData.log['client_id'] = client_id
    except:
        localData.log['client_id'] = 'FAIL'

def user(user_id):
    try:
        localData.log['user_id'] = user_id
    except:
        localData.log['user_id'] = 'FAIL'

def form(data):
    try:
        localData.log['form'] = data
    except:
        localData.log['form'] = 'FAIL'

def attachment(name, size):
    try:
        localData.log['file_name'] = name
        localData.log['file_size'] = size
    except:
        localData.log['file_name'] = 'FAIL'

def output(data):
    try:
        localData.log['output'] = data
    except:
        localData.log['output'] = 'FAIL'

def error(code):
    try:
        localData.log['result'] = code
    except:
        localData.log['result'] = 'FAIL'

    try:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        f = traceback.format_exception(exc_type, exc_value, exc_traceback)
        f = string.joinfields(f, '')
        localData.log['stack_trace'] = f
    except:
        localData.log['stack_trace'] = 'FAIL'

def save():
    if localData.format != 'object':
        # Skip if not an object
        return

    localData.log['finish'] = datetime.datetime.utcnow()

    try:
        if localData.output == None:
            raise
        localData.output(localData.log)
    except:
        pprint.pprint(localData.log)

