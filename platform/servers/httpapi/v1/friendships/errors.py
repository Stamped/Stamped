#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from errors import *

friendship_exceptions = [
    (StampedInvalidFriendshipError, 400, "not_found", "You cannot follow yourself."),
    (StampedFriendshipCheckPermissionsError, 404, "not_found", "Insufficient privileges to check friendship status."),
    (StampedInviteAlreadyExistsError, 403, "illegal_action", "Invite already sent."),
    (StampedUnknownSourceError, 400, "bad_request", "Unknown source name"),
]
