#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from errors import *

entity_exceptions = [
    (StampedEntityUpdatePermissionError, 403, 'invalid_credentials', "Insufficient privileges to update entity"),
    (StampedTombstonedEntityError, 400, 'invalid_credentials', "Sorry, this entity can no longer be updated"),
    (StampedInvalidCategoryError, 400, 'bad_request', "Invalid category"),
    (StampedInvalidSubcategoryError, 400, 'bad_request', "Invalid subcategory"),
    (StampedMenuUnavailableError, 404, 'not_found', "Menu is unavailable"),
]
