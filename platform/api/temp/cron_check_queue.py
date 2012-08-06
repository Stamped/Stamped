#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

import gearman
import datetime
import utils
import tasks.Tasks
import libs.ec2_utils

try:
    errors = []
    hosts = tasks.Tasks.getHosts()
    admin = gearman.admin_client.GearmanAdminClient(hosts)
    queues = admin.get_status()
    for queue in queues:
        if 'queued' in queue and queue['queued'] > 100:
            errors.append(queue)

    if len(errors) > 0 and libs.ec2_utils.is_ec2():
        email = {}
        try:
            stack_info = libs.ec2_utils.get_stack()
            email['subject'] = "%s.%s - WARNING - Queue Backlog" % \
                (stack_info.instance.stack, stack_info.instance.name)
        except Exception:
            email['subject'] = "WARNING - Queue backlog"

        email['body'] = 'The following queues appear to be backlogged:\n\n'
        for error in errors:
            email['body'] += '%s\n\n' % error

        email['from'] = 'Stamped <noreply@stamped.com>'
        email['to'] = 'dev@stamped.com'

        utils.sendEmail(email)
        print '%s | %s' % (datetime.datetime.utcnow(), email)

except Exception as e:
    print '%s | FAILED: %s (%s)' % (datetime.datetime.utcnow(), type(e), e)

