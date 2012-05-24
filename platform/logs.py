#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import datetime, logging, logging.handlers, os, threading, hashlib, random, time
import sys, traceback, string
import inspect, pprint

# Log
log = logging.getLogger('stamped')
log.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Stream handler
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
log.addHandler(stream_handler)

# File handler
try:
    log_file = "/stamped/logs/wsgi.log"
    if os.path.exists(os.path.dirname(log_file)):
        file_handler = logging.handlers.WatchedFileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)
except:
    pass

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
        lineno = inspect.stack()[2][2]
    except:
        fnc = "UNKNOWN FUNCTION"
    
    if localData.format == 'object':
        try:
            msg = str(msg)
        except Exception:
            msg = "LOGGER ERROR: failed to convert msg (type: %s) to string" % type(msg)
        item = (datetime.datetime.utcnow(), level, fnc, lineno, msg)
        localData.log['log'].append(item)
        localData.log[level] = True

    # else:
    msg = "%s | %s | %-25s | %-5s | %s" % (os.getpid(), localData.logId[:6], fnc, lineno, msg)
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
def begin(**kwargs):
    saveLog     = kwargs.pop('saveLog', None)
    saveStat    = kwargs.pop('saveStat', None)
    requestData = kwargs.pop('requestData', None)
    nodeName    = kwargs.pop('nodeName', None)
    
    refresh(format='object')
    
    localData.saveLog  = saveLog
    localData.saveStat = saveStat
    
    if requestData:
        request(requestData)
    
    if nodeName:
        localData.log['node'] = nodeName

def request(request):
    try:
        localData.log['path'] = request.path
        localData.log['method'] = request.method
        localData.log['headers'] = str(request.META)
    except:
        localData.log['request'] = 'FAIL'

def async_request(method, *args, **kwargs):
    try:
        localData.log['path']   = method
        localData.log['method'] = 'ASYNC'
        localData.log['args']   = str(args)
        localData.log['kwargs'] = str(kwargs)
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

def client(client_id):
    try:
        localData.log['client_id'] = client_id
    except:
        localData.log['client_id'] = 'FAIL'

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

def auth(msg):
    try:
        localData.log['auth'] = msg
    except:
        localData.log['auth'] = 'FAIL'

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
        if localData.saveLog == None:
            raise
        localData.saveLog(localData.log)
    except Exception as e:
        pprint.pprint(localData.log)
        pass
    
    try:
        if localData.saveStat is None:
            raise
        localData.saveStat(localData.log)
    except:
        pass

def _report(caller,msg='',level=logging.ERROR):
    caller2 = log.findCaller()
    log.log(level,"REPORT from %s:%s:%s-\t%s\nCALLED by %s:%s:%s",caller2[0],caller2[1],caller2[2],msg,caller[0],caller[1],caller[2],exc_info=True)

def report(*args,**kwargs):
    _report(log.findCaller(),*args,**kwargs)
