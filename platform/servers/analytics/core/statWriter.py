#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals

import calendar, pprint, datetime, sys, math
import keys.aws, logs, utils
import uuid

from MongoStampedAPI                            import MongoStampedAPI
from boto.sdb.connection                        import SDBConnection
from boto.exception                             import SDBResponseError
from gevent.pool                                import Pool


class statWriter(object):
    
    def __init__(self,domain=None):
        self.conn = SDBConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
        self.domain_name = domain
        
    def write(self,stat,key=None,domain=None):
        if domain is None:
            if self.domain_name is None:
                return False
            else:
                domain = self.domain_name
        
        if key is None:
            key = uuid.uuid1()
            
        if len(stat) > 0:
            try:
                domain = self.conn.get_domain(domain)
            except SDBResponseError:
                domain = self.conn.create_domain(domain)
            domain.put_attributes(key, stat, replace=False)
        
        return True