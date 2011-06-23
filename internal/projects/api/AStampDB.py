#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from Stamp import Stamp

class AStampDB(object):
    
    def __init__(self, desc):
        self._desc = desc
    
    def addStamp(self, stamp):
        raise NotImplementedError
    
    def getStamp(self, stampID):
        raise NotImplementedError
    
    def updateStamp(self, stamp):
        raise NotImplementedError
    
    def removeStamp(self, stampID):
        raise NotImplementedError
        
    def flagStamp(self, stampID, flag=1):
        raise NotImplementedError
    
    def addStamps(self, stamps):
        return map(self.addStamp, stamps)
    
    def getStamps(self, stampIDs):
        return map(self.getStamp, stampIDs)
    
    def updateStamps(self, stamps):
        return map(self.updateStamp, stamps)
    
    def removeStamps(self, stampIDs):
        return map(self.removeStamp, stampIDs)
        
    def flagStamps(self, stampIDs, flag=1):
        return map(self.flagStamp, stampIDs, flag)
    
    def __len__(self):
        raise NotImplementedError
    
    def __str__(self):
        return self._desc

