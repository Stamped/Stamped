#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract

class AAccountDB(object):
    
    @abstract
    def addAccount(self, user):
        pass
    
    @abstract
    def getAccount(self, userId):
        pass
    
    @abstract
    def updateAccount(self, user):
        pass
    
    @abstract
    def removeAccount(self, user):
        pass
    
    @abstract
    def flagAccount(self, user):
        pass

    @abstract
    def verifyAccountCredentials(self, screen_name, password):
        pass

