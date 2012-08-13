#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from errors import *

activity_exceptions = [
    (StampedInvalidUniversalNewsItemError, 400, "bad_request", "There was an error adding the activity item."),
]
