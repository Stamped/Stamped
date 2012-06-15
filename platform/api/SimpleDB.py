#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import keys.aws, logs, utils
import os, time, urllib2

from gevent.pool            import Pool
from libs.ec2_utils         import is_ec2, is_prod_stack
from errors                 import *
from bson.objectid          import ObjectId
from boto.sdb.connection    import SDBConnection
from boto.exception         import SDBResponseError

class SimpleDB(object):
    
    def __init__(self, domain=None):
        conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)

        if domain is None:
            if is_prod_stack():
                domain = 'stats-prod'
            elif is_ec2():
                domain = 'stats-dev'
            # else:
            #     domain = 'stats-test'

        try:
            self.domain = conn.get_domain(domain)
        except SDBResponseError:
            self.domain = conn.create_domain(domain)

    def addStat(self, stat):
        if self.domain is None:
            return

        try:
            # Only add specific parameters
            data = {}

            if 'user_id' in stat:
                data['uid'] = stat['user_id']

            if 'path' in stat:
                data['uri'] = stat['path']

            if 'method' in stat:
                data['mtd'] = stat['method']

            if 'form' in stat:
                try:
                    for k, v in stat['form'].items():
                        try:
                            if not isinstance(v, basestring):
                                v = str(v)
                            if len(v.encode('utf-8')) > 1024:
                                v = '<INPUT TOO LONG>'
                            data['frm_%s' % k] = v
                        except Exception as e:
                            print e
                except Exception as e:
                    print e

            if 'result' in stat:
                data['cde'] = str(stat['result'])

            if 'begin' in stat:
                data['bgn'] = stat['begin'].isoformat()

            if 'finish' in stat:
                data['end'] = stat['finish'].isoformat()

            if 'node' in stat:
                data['nde'] = stat['node']

            if len(data) > 0:
                statId = str(ObjectId())
                self.domain.put_attributes(statId, data, replace=False)

        except Exception as e:
            print e
            raise

