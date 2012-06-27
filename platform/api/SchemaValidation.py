#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


import Globals
import logs
import re
from errors             import *
import Entity
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from bson.objectid          import ObjectId

# ########## #
# VALIDATION #
# ########## #

def parsePhoneNumber(phoneStr):
    if phoneStr is not None:
        return re.sub("[^0-9]", "", str(phoneStr))

_color_re = re.compile("^[0-9a-f]{3}(?:[0-9a-f]{3})?$", re.IGNORECASE)
def validateHexColor(color):
    global _color_re
    if color is None:
        return None
    color = color.upper()
    try:
        if _color_re.match(color) is not None:
            return color
        raise
    except:
        logs.warning("Invalid hex color: %s" % color)
        raise StampedInputError("Invalid color value.")

def validateURL(url):
    if url is None or url == "":
        return None
    val = URLValidator(verify_exists=False)
    try:
        val(url)
    except ValidationError, e:
        logs.warning("Invalid URL" % url)
        raise StampedHTTPError(400, msg="Invalid URL")
    return url

def validateObjectId(string):
    if string is None:
        return None
    try:
        r = ObjectId(string)
    except Exception as e:
        logs.warning("Invalid id: %s" % e)
        raise StampedInputError("Invalid id")
    return string

def validateUserId(userId):
    return validateObjectId(userId)

def validateStampId(stampId):
    return validateObjectId(stampId)

def validateViewport(string):
    # Structure: "lat0,lng0,lat1,lng1"
    if string is None:
        return None
    try:
        coords = string.split(',')
        assert(len(coords) == 4)

        lat0 = float(coords[0])
        lng0 = float(coords[1])
        lat1 = float(coords[2])
        lng1 = float(coords[3])

        # Latitudes between -90 and 90
        assert(lat0 >= -90.0 or lat0 <= 90.0)
        assert(lat1 >= -90.0 or lat1 <= 90.0)

        # Longitudes between -180 and 180
        assert(lng0 >= -180.0 or lng0 <- 180.0)
        assert(lng1 >= -180.0 or lng1 <- 180.0)

        return string
    except Exception as e:
        logs.warning("Viewport check failed: %s" % string)

    raise StampedInputError("Invalid viewport: %s" % string)

def validateCategory(category):
    if category is None:
        return None
    try:
        category = category.lower()
        assert(category in Entity.categories)
        return category
    except Exception as e:
        logs.warning("Category check failed for '%s': %s" % (category, e))
        raise StampedInputError("Invalid category: %s" % category)

def validateSubcategory(subcategory):
    if subcategory is None:
        return None
    try:
        subcategory = subcategory.lower()
        assert(subcategory in Entity.subcategories)
        return subcategory
    except Exception as e:
        logs.warning("Subcategory check failed for '%s': %s" % (subcategory, e))
        raise StampedInputError("Invalid subcategory: %s" % subcategory)

_screen_name_re = re.compile("^[\w-]{1,20}$", re.IGNORECASE)
def validateScreenName(screen_name):
    global _screen_name_re
    if screen_name is None:
        return None
    try:
        if _screen_name_re.match(screen_name) and isinstance(screen_name, basestring):
            return screen_name
        raise
    except:
        logs.warning("Invalid screen_name '%s'" % screen_name)
        raise StampedInputError("Invalid screen_name '%s'" % screen_name)