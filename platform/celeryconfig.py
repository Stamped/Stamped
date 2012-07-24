#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import stamped
import utils, logs
import libs.ec2_utils
import multiprocessing, os, sys

from datetime import timedelta
from celery.schedules import crontab

# List of modules to import when celery starts.
CELERY_IMPORTS = ("tasks", )

## Result store settings.
CELERY_RESULT_BACKEND = "amqp"

host, port = "localhost", 5672
user, password, vhost = "guest", "guest", "/"

if utils.is_ec2():
    stack = libs.ec2_utils.get_stack()
    
    for node in stack.nodes:
        if 'monitor' in node.roles:
            host = node.private_ip_address
            break

## Broker settings.
BROKER_URL = "amqp://%s:%s@%s:%s/%s" % (user, password, host, port, vhost)
logs.info('BROKER_URL: %s' % BROKER_URL)

CELERYD_POOL = 'gevent'

if utils.is_ec2():
    CELERYD_CONCURRENCY  = multiprocessing.cpu_count() * 2 + 1

# use default concurrency; uncomment to use a single celeryd worker
# (can be useful for debugging)
#CELERYD_CONCURRENCY = 1

# Always run tasks locally / synchronously, completely bypassing the async 
# brokering / work queues that Celery provides. Note that this can be extremely 
# useful for debugging.
#CELERY_ALWAYS_EAGER = True

# -----------------------------------------------------------------------------

# Enables error emails
CELERY_SEND_TASK_ERROR_EMAILS = True

# Name and email addresses of recipients
ADMINS = (
    ("stamped-dev", "dev@stamped.com"), 
)

# Email address used as sender (From field).
SERVER_EMAIL = "notifications@stamped.com"

# Mailserver configuration
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_SSL = False
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "notifications@stamped.com"
EMAIL_HOST_PASSWORD = "mariotennis"

CELERY_QUEUES = {
    "default": {
        "exchange": "default",
        "binding_key": "default"
    },
    "api": {
        "exchange": "stamped",
        "exchange_type": "topic",
        "binding_key": "api.#",
    },
    "enrich": {
        "exchange": "stamped",
        "exchange_type": "topic",
        "binding_key": "enrich.#",
    }
}
CELERY_DEFAULT_QUEUE = "default"
CELERY_DEFAULT_EXCHANGE_TYPE = "direct"
CELERY_DEFAULT_ROUTING_KEY = "default"

CELERYBEAT_SCHEDULE = {
    'rss-crawlers' : {
        'task' : 'tasks.APITasks.crawlExternalSources',
        'schedule' : timedelta(hours=3),
        'relative' : True,
    },
    'make-new-autocomplete-index' : {
        'task' : 'tasks.APITasks.updateAutoCompleteIndex',
        'schedule' : crontab(hour=4, minute=0),
    },
}

