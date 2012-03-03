#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract

class AAuthEmailAlertsDB(object):

    @abstract
    def addToken(self, token):
        pass

    @abstract
    def getTokenForUser(self, userId):
        pass

    @abstract
    def getTokensForUsers(self, userIds, limit=0):
        pass
    
    @abstract
    def getToken(self, tokenId):
        pass
        
    @abstract
    def removeTokenForUser(self, userId):
        pass
        
    @abstract
    def removeToken(self, tokenId):
        pass
    
