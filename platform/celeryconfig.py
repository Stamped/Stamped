#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import stamped
import utils
import libs.ec2_utils

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
utils.log('BROKER_URL: %s' % BROKER_URL)

# use default concurrency; uncomment to use a single celeryd worker
# (can be useful for debugging)
#CELERYD_CONCURRENCY = 1

"""
# Enables error emails (note: haven't been able to get these error emails to actuall work).
CELERY_SEND_TASK_ERROR_EMAILS = True

# Name and email addresses of recipients
ADMINS = (
    ("stamped-dev", "dev@stamped.com"), 
)

# Email address used as sender (From field).
SERVER_EMAIL = "notifications@stamped.com"

# Mailserver configuration
# TODO: Error emails aren't working
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_SSL = True
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "notifications@stamped.com"
EMAIL_HOST_PASSWORD = "mariotennis"
"""

# Always run tasks locally / synchronously, completely bypassing the async brokering / work queues
# that Celery provides. Note that this can be extremely useful for debugging.
#CELERY_ALWAYS_EAGER = True

