#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract

class AAuthPasswordResetDB(object):
    
    @abstract
    def addResetToken(self, token):
        pass
    
    @abstract
    def getResetToken(self, tokenId):
        pass
    
    @abstract
    def removeResetToken(self, tokenId):
        pass

