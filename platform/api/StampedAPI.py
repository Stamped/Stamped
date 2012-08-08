#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from logs import report

try:
    import utils
    import os
    import logs
    import re
    import time
    import urlparse
    import math
    import pylibmc
    import gevent
    import traceback
    import random

    from utils import lazyProperty, LoggingThreadPool

    from api.accounts import Accounts
    from api.users import Users
    from api.friendships import Friendships
    from api.entities import Entities
    from api.stamps import Stamps
    from api.guides import Guides
    from api.likeapi import LikeAPI
    from api.comments import Comments
    from api.todos import Todos

except Exception as e:
    report()
    raise


class StampedAPI(object):



    @lazyProperty
    def node_name(self):
        try:
            stack_info = libs.ec2_utils.get_stack()
            return "%s.%s" % (stack_info.instance.stack, stack_info.instance.name)
        except Exception as e:
            return "unknown"

    @lazyProperty
    def accounts(self):
        return Accounts()

    @lazyProperty
    def users(self):
        return Users()

    @lazyProperty
    def friendships(self):
        return Friendships()

    @lazyProperty
    def entities(self):
        return Entities()

    @lazyProperty
    def stamps(self):
        return Stamps()

    @lazyProperty
    def guides(self):
        return Guides()

    @lazyProperty
    def likes(self):
        return LikeAPI()

    @lazyProperty
    def comments(self):
        return Comments()

    @lazyProperty
    def todos(self):
        return Todos()
