#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from abc import abstractmethod
from Stamp import Stamp

class AStampDB(object):
    
    def __init__(self, desc):
        self._desc = desc
    
    @abstractmethod
    def addStamp(self, stamp):
        pass
        
    @abstractmethod
    def getStamp(self, stampId):
        pass
        
    @abstractmethod
    def updateStamp(self, stamp):
        pass
        
    @abstractmethod
    def removeStamp(self, stamp):
        pass
        
    @abstractmethod
    def addStamps(self, stamps):
        pass
        
    @abstractmethod
    def getStamps(self, stampIds):
        pass
    