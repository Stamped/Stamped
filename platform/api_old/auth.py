#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import datetime, time, random, hashlib, string
import utils

def convertPasswordForStorage(password):
    chars = 'ABCDEFGHIJKLMNOPQRSTUVXYZ0123456789abcdefghijklmnopqrstuvwxyz'
    salt = ''.join(random.choice(chars) for i in range(6))
    h = hashlib.md5()
    h.update(salt)
    h.update(password.encode('ascii', 'xmlcharrefreplace'))
    ret = salt + h.hexdigest()
    return ret

def comparePasswordToStored(password, stored):
    try:
        salt = stored[:6]
        h = hashlib.md5()
        h.update(salt)
        h.update(password.encode('ascii', 'xmlcharrefreplace'))
        if salt + h.hexdigest() == stored:
            return True
        return False
    except:
        return False

def generateToken(length):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for x in xrange(length))

