#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import datetime, logging, threading, hashlib, random, time

# Log
log = logging.getLogger('stamped')
log.setLevel(logging.WARNING)

# Formatter
formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%H:%M:%S')

# Stream handler
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
ch.setFormatter(formatter)

# Add handler
log.addHandler(ch)

def _generateLogId():
    m = hashlib.md5(str(time.time()))
    m.update(str(random.random()))
    return str(m.hexdigest())[:6]

def refresh():
    localData.logId = _generateLogId()

localData = threading.local()
refresh()


def formatMessage(msg):
    import inspect
    fnc = inspect.stack()[2][3]
    try:
        localData.logId
    except:
        refresh()
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

