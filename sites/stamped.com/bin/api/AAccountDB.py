#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from abc import abstractmethod
from Account import Account

class AAccountDB(object):
    
    def __init__(self, desc):
        self._desc = desc
        
    @abstractmethod
    def addAccount(self, user):
        pass
        
    @abstractmethod
    def getAccount(self, userId):
        pass
        
    @abstractmethod
    def updateAccount(self, user):
        pass
        
    @abstractmethod
    def removeAccount(self, user):
        pass
        
    @abstractmethod
    def flagAccount(self, user):
        pass

