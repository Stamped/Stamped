#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from errors import *

account_exceptions = [
    (StampedInvalidEmailError,              400, 'invalid_credentials', "Invalid email address"),
    (StampedInvalidScreenNameError,         400, 'invalid_credentials', "Invalid username"),
    (StampedScreenNameInUseError,           400, 'invalid_credentials', "Username is already in use"),
    (StampedBlackListedScreenNameError,     403, 'forbidden',           'Invalid username'),
    (StampedInvalidPasswordError,           403, 'invalid_credentials', 'Incorrect password'),
    (StampedInvalidWebsiteError,            403, 'invalid_credentials', "Could not update account website"),
    (StampedInvalidStampColorsError,        403, 'invalid_credentials', "Invalid stamp colors"),
    (StampedDuplicateEmailError,            409, 'invalid_credentials', "An account already exists with that email address"),
    (StampedDuplicateScreenNameError,       409, 'invalid_credentials', "An account already exists with that username"),
    (StampedAccountNotFoundError,           404, 'not_found',           'There was an error retrieving account information'),
    (StampedAlreadyStampedAuthError,        400, 'bad_request',         'This account is already a Stamped account'),
    (StampedLinkedAccountMismatchError,     400, 'illegal_action',      "There was a problem verifying the third-party account"),
    (StampedUnsetRequiredFieldError,        400, 'illegal_action',      "Cannot remove a required account field"),
    (StampedEmailInUseError,                400, 'invalid_credentials', "Email address is already in use"),
]
