#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals
import utils
import libs.ec2_utils

# List of modules to import when celery starts.
CELERY_IMPORTS = ("api", )

## Result store settings.
CELERY_RESULT_BACKEND = "amqp"

host, port = "localhost", 5672
user, password, vhost = "test", "mariotennis", "stampedvhost"

if utils.is_ec2():
    stack = libs.ec2_utils.get_stack()
    
    for node in stack.nodes:
        if 'monitor' in node.roles:
            host, port = node.private_ip_address, 5672

## Broker settings.
BROKER_URL = "amqp://%s:%s@%s:%s/%s" % (user, password, host, port, vhost)

## Worker settings
## If you're doing mostly I/O you can have more processes,
## but if mostly spending CPU, try to keep it close to the
## number of CPUs on your machine. If not set, the number of CPUs/cores
## available will be used.
#CELERYD_CONCURRENCY = 1

"""
CELERY_RESULT_BACKEND = "mongodb"
CELERY_MONGODB_BACKEND_SETTINGS = {
    "host": "192.168.1.100",
    "port": 27017,
    "database": "stamped",
    "taskmeta_collection": "tasks",
}
"""

# Name and email addresses of recipients
ADMINS = (
    ("stamped-dev", "dev@stamped.com"), 
)

# Enables error emails.
CELERY_SEND_TASK_ERROR_EMAILS = True

# Email address used as sender (From field).
SERVER_EMAIL = "notifications@stamped.com"

# Mailserver configuration
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "notifications@stamped.com"
EMAIL_HOST_PASSWORD = "mariotennis"

