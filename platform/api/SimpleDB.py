#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import keys.aws, logs, utils
import os, time, urllib2

from libs.ec2_utils         import is_ec2, is_prod_stack
from errors                 import *
from bson.objectid          import ObjectId
from boto.sdb.connection    import SDBConnection
from boto.exception         import SDBResponseError
from hashlib                import sha1

class SimpleDB(object):
    
    def __init__(self, domain=None):
        self.conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
        self.domain_name = None
        self.domains = {}

        if domain is None:
            if is_prod_stack():
                self.domain_name = 'stats_prod'
            elif is_ec2():
                self.domain_name = 'stats_dev'
        else:
            self.domain_name = domain

    def addStat(self, stat):
        if self.domain_name is None:
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
                
            if 'client_id' in stat:
                data['cid'] = stat['client_id']

            if len(data) > 0:
                statId = str(ObjectId())
                if data['uri'] != '/v1/ping.json' and data['uri'] != '/v1/temp/ping.json':
                    suffix = '0%s' % (sha1(statId).hexdigest()[0])
                    if suffix in self.domains:
                        domain = self.domains[suffix]
                    else:
                        try:
                            domain = self.conn.get_domain('%s_%s' % (self.domain_name, suffix))
                        except SDBResponseError:
                            domain = self.conn.create_domain('%s_%s' % (self.domain_name, suffix))
                        self.domains[suffix] = domain
                    domain.put_attributes(statId, data, replace=False)


        except Exception as e:
            print e
            raise
