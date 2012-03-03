#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract

class AUserDB(object):
    
    @abstract
    def getUser(self, userId):
        pass
        
    @abstract
    def getUserByScreenName(self, screenName):
        pass

    @abstract
    def lookupUsers(self, userIds, usernames, limit=0):
        pass
        
    @abstract
    def searchUsers(self, query, limit=20, relationship=None):
        pass
        
    @abstract
    def flagUser(self, user):
        pass
        
    @abstract
    def updateUserStats(self, userId, stat, value=None, increment=1):
        pass

