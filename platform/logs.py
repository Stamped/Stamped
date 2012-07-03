#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import datetime, logging, logging.handlers, os, threading, hashlib, random, time
import sys, traceback, string, utils
import inspect, pprint

# Log
log = logging.getLogger('stamped')
log.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Stream handler
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
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


class LoggingContext(object):
    def __init__(self, format=None):
        self.__format = format
        self.__logId = self.__generateLogId()
        self.__log = {
            'log': [],
            'begin': datetime.datetime.utcnow(),
            'request_id': self.__logId
        }

    def save(self):
        if self.__format != 'object':
            return

        self.__log['finish'] = datetime.datetime.utcnow()

        try:
            localData.saveStat(localData.log)
        except:
            pass

        try:
            localData.saveLog(localData.log)
        except Exception as e:
            pprint.pprint(localData.log)
            pass

    @classmethod
    def __generateLogId(cls):
        m = hashlib.md5(str(time.time()))
        m.update(str(random.random()))
        return str(m.hexdigest())

    def addLogParameter(self, key, value):
        self.__log[key] = value

    def appendToLog(self, item):
        self.__log['log'].append(item)

    def log(self, level, msg, *args, **kwargs):
        try:
            filename    = inspect.stack()[2][1]
            if filename.rfind('/') != -1:
                filename = filename[filename.rfind('/') + 1:]
            lineno      = inspect.stack()[2][2]
            fnc         = inspect.stack()[2][3]
        except:
            fnc = "UNKNOWN FUNCTION"
            filename = "UNKNOWN FILENAME"
            lineno = "UNKNOWN LINENO"

        if self.__format == 'object':
            try:
                msg = unicode(msg)
            except Exception:
                msg = "LOGGER ERROR: failed to convert msg (type: %s) to string" % type(msg)
            item = (datetime.datetime.utcnow(), level, filename, lineno, fnc, msg)
            self.appendToLog(item)
            self.addLogParameter(level, True)


        if isinstance(msg, unicode):
            msg = msg.encode('utf-8')

        # else:
        msg = "{0} | {1} | {2:25}:{3:>5} | {4} | {5}".format(os.getpid(), self.__logId[:6], filename, lineno, fnc, msg)
        if level == 'warning':
            log.warning(msg, *args, **kwargs)
        elif level == 'info':
            log.info(msg, *args, **kwargs)
        else:
            log.debug(msg, *args, **kwargs)



def _getLoggingContext(forceCreate=False):
    if not forceCreate:
        return localData.loggingContext
    else:
        try:
            return localData.loggingContext
        except AttributeError:
            localData.loggingContext = LoggingContext()
            return localData.loggingContext

def refresh(format=None):
    localData.loggingContext = LoggingContext(format=format)
    return localData.loggingContext

localData = threading.local()
refresh()

def _log(level, msg, *args, **kwargs):
    _getLoggingContext(forceCreate=True).log(level, msg, *args, **kwargs)

def runInOtherLoggingContext(fn, context):
    oldLoggingContext = _getLoggingContext(forceCreate=True)
    localData.loggingContext = context
    try:
        return fn()
    finally:
        localData.loggingContext = oldLoggingContext

def formatMessage(msg, fnc):
    msg = "%s | %-25s | %s" % (_getLoggingContext().logId, fnc, msg)
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
    loggingContext = refresh(format='object')
    # Pretty hacky.
    loggingContext.saveLog = kwargs.pop('saveLog', None)
    loggingContext.saveStat = kwargs.pop('saveStat', None)

    requestData = kwargs.pop('requestData', None)
    nodeName    = kwargs.pop('nodeName', None)
    
    if requestData:
        request(requestData)
    
    if nodeName:
        loggingContext.addLogParameter('node', nodeName)

def request(request):
    loggingContext = _getLoggingContext()
    try:
        loggingContext.addLogParameter('path', request.path)
        loggingContext.addLogParameter('method', request.method)
        loggingContext.addLogParameter('headers', request.META)
    except:
        loggingContext.addLogParameter('request', 'FAIL')

def async_request(method, *args, **kwargs):
    loggingContext = _getLoggingContext()
    try:
        loggingContext.addLogParameter('path', method)
        loggingContext.addLogParameter('method', 'ASYNC')
        loggingContext.addLogParameter('args', str(args))
        loggingContext.addLogParameter('kwargs', str(kwargs))
    except:
        loggingContext.addLogParameter('request', 'FAIL')

def token(token):
    _getLoggingContext().addLogParameter('token', token)

def user(user_id):
    _getLoggingContext().addLogParameter('user_id', user_id)

def client(client_id):
    _getLoggingContext().addLogParameter('client_id', client_id)

def form(data):
    _getLoggingContext().addLogParameter('form', data)

def attachment(name, size):
    loggingContext = _getLoggingContext()
    loggingContext.addLogParameter('file_name', name)
    loggingContext.addLogParameter('file_size', size)

def output(data):
    _getLoggingContext().addLogParameter('output', data)

def auth(msg):
    _getLoggingContext().addLogParameter('auth', msg)

def error(code):
    loggingContext = _getLoggingContext()
    loggingContext.addLogParameter('result', code)
    try:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        f = traceback.format_exception(exc_type, exc_value, exc_traceback)
        f = string.joinfields(f, '')
        loggingContext.addLogParameter('stack_trace', f)
    except:
        loggingContext.addLogParameter('stack_trace', 'FAIL')

def save():
    _getLoggingContext().save()

def _report(caller,msg='',level=logging.ERROR):
    caller2 = log.findCaller()
    log.log(level,"REPORT from %s:%s:%s-\t%s\nCALLED by %s:%s:%s",caller2[0],caller2[1],caller2[2],msg,caller[0],caller[1],caller[2],exc_info=True)

def report(*args,**kwargs):
    _report(log.findCaller(),*args,**kwargs)