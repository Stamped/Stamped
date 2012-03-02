#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract

class AAuthAccessTokenDB(object):
    
    @abstract
    def addAccessToken(self, token):
        pass
    
    @abstract
    def getAccessToken(self, tokenId):
        pass
    
    @abstract
    def removeAccessToken(self, tokenId):
        pass

