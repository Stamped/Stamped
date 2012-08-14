#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from errors import *

oauth_exceptions = [
    (StampedInvalidAuthTokenError, 401, 'invalid_token', None),
    (StampedInvalidRefreshTokenError, 401, 'invalid_token', None),
    (StampedInvalidClientError, 401, 'invalid_client', None),
    (StampedGrantTypeIncorrectError, 400, 'invalid_grant', None),
    (StampedAccountNotFoundError, 401, 'invalid_credentials',  "The username / password combination is incorrect"),
    (StampedInvalidCredentialsError, 401, 'invalid_credentials',  "The username / password combination is incorrect"),
]
