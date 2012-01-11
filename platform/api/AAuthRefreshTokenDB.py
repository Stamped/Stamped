#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract

class AAuthRefreshTokenDB(object):
    
    @abstract
    def addRefreshToken(self, token):
        pass
    
    @abstract
    def getRefreshToken(self, tokenId):
        pass
    
    @abstract
    def removeRefreshToken(self, tokenId):
        pass

