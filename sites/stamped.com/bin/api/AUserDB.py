#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from utils import abstract
from User import User

class AUserDB(object):
    
    @abstract
    def getUser(self, userID):
        pass
        
    @abstract
    def lookupUsers(self, userIDs, usernames):
        pass
        
    @abstract
    def searchUsers(self, searchQuery, searchLimit=20):
        pass
        
    @abstract
    def checkPrivacy(self, userId):
        pass
        
