#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract

class AStampDB(object):
    
    @abstract
    def addStamp(self, stamp):
        pass
        
    @abstract
    def getStamp(self, stampId):
        pass
        
    @abstract
    def updateStamp(self, stamp):
        pass
        
    @abstract
    def removeStamp(self, stamp):
        pass
        
    @abstract
    def addStamps(self, stamps):
        pass
        
    @abstract
    def getStamps(self, stampIds):
        pass

    @abstract
    def addUserStampReference(self, userId, stampId):
        pass
        
    @abstract
    def removeUserStampReference(self, userId, stampId):
        pass

    @abstract
    def addInboxStampReference(self, userIds, stampId):
        pass

    @abstract
    def removeInboxStampReference(self, userIds, stampId):
        pass
    
    @abstract
    def incrementStatsForStamp(self, stampId, stat, increment=1):
        pass

    @abstract
    def giveCredit(self, creditedUserId, stamp):
        pass
