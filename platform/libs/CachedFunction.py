#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

"""
Defines a decorator for functions that are going to be cached. Uses either memcached_function if we're on ec2, or
mongoCachedFn otherwise.
"""

import datetime, functools, utils
from Memcache import memcached_function
from MongoCache import mongoCachedFn

ONE_WEEK = 7*24*60*60
def cachedFn(ttl=ONE_WEEK):
    if utils.is_ec2():
        return memcached_function(time=ttl)
    else:
        return mongoCachedFn(maxStaleness=datetime.timedelta(0, ttl))