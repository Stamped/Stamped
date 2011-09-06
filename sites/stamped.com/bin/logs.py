#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import datetime, logging, os, threading, hashlib, random, time
import inspect

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
    return str(m.hexdigest())[:6]

def refresh():
    localData.logId = _generateLogId()

localData = threading.local()
refresh()

def formatMessage(msg):
    try:
        localData.logId
    except:
        refresh()
    
    try:
        fnc = inspect.stack()[2][3]
    except:
        fnc = ""
    
    msg = "%s | %-25s | %s" % (localData.logId, fnc, msg)
    return msg

# Logging Functions
def info(msg, *args, **kwargs):
    msg = formatMessage(msg)
    log.info(msg, *args, **kwargs)

def debug(msg, *args, **kwargs):
    msg = formatMessage(msg)
    log.debug(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    msg = formatMessage(msg)
    log.warning(msg, *args, **kwargs)

# Alternate
def warn(msg, *args, **kwargs):
    warning(msg, *args, **kwargs)

