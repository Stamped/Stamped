#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract

class AFriendshipDB(object):
    
    def addFriendship(self, friendship):
        pass
    
    @abstract
    def checkFriendship(self, friendship):
        pass
    
    @abstract
    def removeFriendship(self, friendship):
        pass
    
    @abstract
    def getFriends(self, userId):
        pass
    
    @abstract
    def getFollowers(self, userId):
        pass
    
    @abstract
    def approveFriendship(self, friendship):
        pass
    
    @abstract
    def addBlock(self, friendship):
        pass
    
    @abstract
    def checkBlock(self, friendship):
        pass
    
    @abstract
    def removeBlock(self, friendship):
        pass
    
    @abstract
    def getBlocks(self, userId):
        pass

