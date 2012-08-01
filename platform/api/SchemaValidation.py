#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


import Globals
import logs
import re
from errors             import *
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from api          import Constants

from bson.objectid          import ObjectId

# ########## #
# VALIDATION #
# ########## #

def parsePhoneNumber(phoneStr):
    if phoneStr is not None:
        return re.sub("[^0-9]", "", unicode(phoneStr))
    return None

_color_re = re.compile("^[0-9a-f]{3}(?:[0-9a-f]{3})?$", re.IGNORECASE)
def validateHexColor(color):
    global _color_re
    if color is None or color == '':
        return None
    color = color.upper()
    try:
        if _color_re.match(color) is not None:
            return color
        raise
    except:
        logs.warning("Invalid hex color: %s" % color)
        raise StampedInvalidColorError("Invalid color value.")

def validateString(string):
    if string is None or string == '':
        return None 
    if isinstance(string, basestring):
        return string
    try: 
        return unicode(string)
    except Exception as e:
        logs.warning("Invalid string: %s (%s)" % (string, e))
        raise StampedInputError("Invalid string")

def validateURL(url):
    if url is None or url == '':
        return None
    val = URLValidator(verify_exists=False)
    try:
        val(url)
    except ValidationError, e:
        raise StampedInvalidURLError("Invalid URL: %s" % url)
    return url

def validateObjectId(string):
    if string is None or string == '':
        return None
    try:
        r = ObjectId(string)
    except Exception as e:
        logs.warning("Invalid id: %s" % e)
        raise StampedObjectIdError("Invalid id")
    return string

def validateUserId(userId):
    return validateObjectId(userId)

def validateStampId(stampId):
    return validateObjectId(stampId)

def validateCoordinates(string):
    # Structure: "lat0,lng0"
    if string is None or string == '':
        return None
    try:
        coords = string.split(',')
        assert(len(coords) == 2)

        lat = float(coords[0])
        lng = float(coords[1])

        # Latitude between -90 and 90
        assert(lat >= -90.0 or lat <= 90.0)

        # Longitude between -180 and 180
        assert(lng >= -180.0 or lng <- 180.0)

        return string
    except Exception as e:
        logs.warning("Coordinates check failed: %s" % string)

    raise StampedInputError("Invalid coordinates: %s" % string)

def validateViewport(string):
    # Structure: "lat0,lng0,lat1,lng1"
    if string is None or string == '':
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
    if category is None or category == '':
        return None
    try:
        category = category.lower()
        assert(category in Constants.categories)
        return category
    except Exception as e:
        logs.warning("Category check failed for '%s': %s" % (category, e))
        raise StampedInputError("Invalid category: %s" % category)

def validateSubcategory(subcategory):
    if subcategory is None or subcategory == '':
        return None
    try:
        subcategory = subcategory.lower()
        assert(subcategory in Constants.subcategories)
        return subcategory
    except Exception as e:
        logs.warning("Subcategory check failed for '%s': %s" % (subcategory, e))
        raise StampedInputError("Invalid subcategory: %s" % subcategory)

_screen_name_re = re.compile("^[\w-]{1,20}$", re.IGNORECASE)
def validateScreenName(screen_name):
    global _screen_name_re
    if screen_name is None or screen_name == '':
        return None
    try:
        if _screen_name_re.match(screen_name) and isinstance(screen_name, basestring):
            return screen_name
        raise
    except:
        raise StampedInvalidScreenNameError("Invalid screen_name '%s'" % screen_name)


__email_re = re.compile(
    R"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"               # dot-atom
    R'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    R')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)   # domain
def validateEmail(email):
    if email is None or email == '':
        return None
    # Source: http://data.iana.org/TLD/tlds-alpha-by-domain.txt
    # Version 2012012600, Last Updated Thu Jan 26 15:07:01 2012 UTC
    valid_suffixes = set(["AC", "AD", "AE", "AERO", "AF", "AG", "AI", "AL", "AM", "AN", "AO", "AQ", "AR", "ARPA", "AS",
                          "ASIA", "AT", "AU", "AW", "AX", "AZ", "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BIZ", "BJ", "BM", "BN",
                          "BO", "BR", "BS", "BT", "BV", "BW", "BY", "BZ", "CA", "CAT", "CC", "CD", "CF", "CG", "CH", "CI", "CK", "CL",
                          "CM", "CN", "CO", "COM", "COOP", "CR", "CU", "CV", "CW", "CX", "CY", "CZ", "DE", "DJ", "DK", "DM", "DO", "DZ",
                          "EC", "EDU", "EE", "EG", "ER", "ES", "ET", "EU", "FI", "FJ", "FK", "FM", "FO", "FR", "GA", "GB", "GD", "GE",
                          "GF", "GG", "GH", "GI", "GL", "GM", "GN", "GOV", "GP", "GQ", "GR", "GS", "GT", "GU", "GW", "GY", "HK", "HM",
                          "HN", "HR", "HT", "HU", "ID", "IE", "IL", "IM", "IN", "INFO", "INT", "IO", "IQ", "IR", "IS", "IT", "JE", "JM",
                          "JO", "JOBS", "JP", "KE", "KG", "KH", "KI", "KM", "KN", "KP", "KR", "KW", "KY", "KZ", "LA", "LB", "LC", "LI",
                          "LK", "LR", "LS", "LT", "LU", "LV", "LY", "MA", "MC", "MD", "ME", "MG", "MH", "MIL", "MK", "ML", "MM", "MN",
                          "MO", "MOBI", "MP", "MQ", "MR", "MS", "MT", "MU", "MUSEUM", "MV", "MW", "MX", "MY", "MZ", "NA", "NAME", "NC",
                          "NE", "NET", "NF", "NG", "NI", "NL", "NO", "NP", "NR", "NU", "NZ", "OM", "ORG", "PA", "PE", "PF", "PG", "PH",
                          "PK", "PL", "PM", "PN", "PR", "PRO", "PS", "PT", "PW", "PY", "QA", "RE", "RO", "RS", "RU", "RW", "SA", "SB",
                          "SC", "SD", "SE", "SG", "SH", "SI", "SJ", "SK", "SL", "SM", "SN", "SO", "SR", "ST", "SU", "SV", "SX", "SY",
                          "SZ", "TC", "TD", "TEL", "TF", "TG", "TH", "TJ", "TK", "TL", "TM", "TN", "TO", "TP", "TR", "TRAVEL", "TT",
                          "TV", "TW", "TZ", "UA", "UG", "UK", "US", "UY", "UZ", "VA", "VC", "VE", "VG", "VI", "VN", "VU", "WF", "WS",
                          "XN--0ZWM56D", "XN--11B5BS3A9AJ6G", "XN--3E0B707E", "XN--45BRJ9C", "XN--80AKHBYKNJ4F", "XN--90A3AC",
                          "XN--9T4B11YI5A", "XN--CLCHC0EA0B2G2A9GCD", "XN--DEBA0AD", "XN--FIQS8S", "XN--FIQZ9S", "XN--FPCRJ9C3D",
                          "XN--FZC2C9E2C", "XN--G6W251D", "XN--GECRJ9C", "XN--H2BRJ9C", "XN--HGBK6AJ7F53BBA", "XN--HLCJ6AYA9ESC7A",
                          "XN--J6W193G", "XN--JXALPDLP", "XN--KGBECHTV", "XN--KPRW13D", "XN--KPRY57D", "XN--LGBBAT1AD8J", "XN--MGBAAM7A8H",
                          "XN--MGBAYH7GPA", "XN--MGBBH1A71E", "XN--MGBC0A9AZCG", "XN--MGBERP4A5D4AR", "XN--O3CW4H", "XN--OGBPF8FL",
                          "XN--P1AI", "XN--PGBS0DH", "XN--S9BRJ9C", "XN--WGBH1C", "XN--WGBL6A", "XN--XKC2AL3HYE2A", "XN--XKC2DL3A5EE0H",
                          "XN--YFRO4I67O", "XN--YGBI2AMMX", "XN--ZCKZAH", "XXX", "YE", "YT", "ZA", "ZM", "ZW"])
    try:
        if __email_re.match(email):
            if email.split('.')[-1].upper() in valid_suffixes:
                return email
    except:
        pass

    raise StampedInvalidEmailError("Invalid format for email address: %s" % email)

def validateEmails(emails):
    emails = validateString(emails)

    if emails is None or emails == '':
        return None

    for email in emails.split(','):
        r = validateEmail(email)

    return emails
