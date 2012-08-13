#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

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

    from api.accountapi import AccountAPI
    from api.userapi import UserAPI
    from api.friendshipapi import FriendshipAPI
    from api.entityapi import EntityAPI
    from api.stampapi import StampAPI
    from api.guideapi import GuideAPI
    from api.likeapi import LikeAPI
    from api.commentapi import CommentAPI
    from api.todoapi import TodoAPI

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
        return AccountAPI()

    @lazyProperty
    def users(self):
        return UserAPI()

    @lazyProperty
    def friendships(self):
        return FriendshipAPI()

    @lazyProperty
    def entities(self):
        return EntityAPI()

    @lazyProperty
    def stamps(self):
        return StampAPI()

    @lazyProperty
    def guides(self):
        return GuideAPI()

    @lazyProperty
    def likes(self):
        return LikeAPI()

    @lazyProperty
    def comments(self):
        return CommentAPI()

    @lazyProperty
    def todos(self):
        return TodoAPI()
