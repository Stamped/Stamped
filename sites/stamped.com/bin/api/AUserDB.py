#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from abc import abstractmethod
from User import User

class AUserDB(object):
    
    def __init__(self, desc):
        self._desc = desc
        
    @abstractmethod
    def getUser(self, userID):
        pass
        
    @abstractmethod
    def lookupUsers(self, userIDs, usernames):
        pass
        
    @abstractmethod
    def searchUsers(self, searchQuery, searchLimit=20):
        pass
        
    @abstractmethod
    def checkPrivacy(self, userId):
        pass
        
