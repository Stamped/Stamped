#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

"""
Defines a decorator for functions that are going to be cached. Uses either memcached_function if we're on ec2, or
mongoCachedFn otherwise.
"""

import datetime, functools, utils
from libs.Memcache import memcached_function
from libs.MongoCache import mongoCachedFn

ONE_WEEK = 7*24*60*60

def cachedFn(ttl=ONE_WEEK, memberFn=True, schemaClasses=[]):
    """
    Decorator that wraps a function in a caching layer, using either Memcache if operating in production or MongoCache
    if running on a development machine.

    ttl determines how long, in seconds, results will be stored in the cache before being invalidated.
    memberFn should be set to False when the wrapped function is not a member function.
    schemaClasses should be a list of the actual schema classes that we expect to be returned within the response. So,
      for instance, you might decorate a function with @cachedFn(schemaClasses=[User,Entity]) if you expected it to
      return a user and a list of entities on their to-do list.
    """
    if utils.is_ec2():
        return memcached_function(time=ttl)
    else:
        return mongoCachedFn(maxStaleness=datetime.timedelta(0, ttl), memberFn=memberFn, schemaClasses=schemaClasses)

def devOnlyCachedFn(memberFn=True, schemaClasses=[]):
    """
    Decorator that wraps a function in a Mongo-based caching layer only if running on a development machine.

    Meanings of memberFn and schemaClasses are as with cachedFn decorator above.
    """
    if utils.is_ec2():
        return lambda wrappedFn: wrappedFn
    else:
        return mongoCachedFn(maxStaleness=datetime.timedelta(0, ttl), memberFn=memberFn, schemaClasses=schemaClasses)