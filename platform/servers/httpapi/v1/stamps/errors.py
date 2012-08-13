#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from errors import *

stamp_exceptions = [
    (StampedAccountNotFoundError, 404, 'not_found', 'There was an error retrieving account information'),
    (StampedOutOfStampsError, 403, 'forbidden', 'No more stamps remaining'),
    (StampedNotLoggedInError, 401, 'bad_request', 'You must be logged in to perform this action.'),
    (StampedRemoveStampPermissionsError, 403, 'forbidden', 'Insufficient privileges to remove stamp'),
    (StampedViewStampPermissionsError, 403, "forbidden", "Insufficient privileges to view stamp"),
    (StampedAddCommentPermissionsError, 403, "forbidden", "Insufficient privileges to add comment"),
    (StampedRemoveCommentPermissionsError, 403, "forbidden", "Insufficient privileges to remove comment"),
    (StampedViewCommentPermissionsError, 403, "forbidden", "Insufficient privileges to view comment"),
    (StampedPermissionsError, 403, "forbidden", "Insufficient privileges to view stamp"),
    (StampedBlockedUserError, 403, 'forbidden', "User is blocked"),
]
