#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import datetime, time, random, hashlib
import utils

def generatePasswordHash(password):
    chars = 'ABCDEFGHIJKLMNOPQRSTUVXYZ0123456789abcdefghijklmnopqrstuvwxyz'
    salt = ''.join(random.choice(chars) for i in range(6))
    h = hashlib.md5()
    h.update(salt)
    h.update(password)
    ret = salt + h.hexdigest()
    return ret

def comparePasswordToHash(password, passwordHash):
    try:
        salt = passwordHash[:6]
        h = hashlib.md5()
        h.update(salt)
        h.update(password)
        if salt + h.hexdigest() == passwordHash:
            return True
        return False
    except:
        return False