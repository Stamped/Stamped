#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from Friendship import Friendship

class AFriendshipDB(object):
    
    def __init__(self, desc):
        self._desc = desc
    
    def addFriendship(self, friendship):
        raise NotImplementedError
    
    def checkFriendship(self, friendship):
        raise NotImplementedError
    
    def removeFriendship(self, friendship):
        raise NotImplementedError
    
    def getFriends(self, userId):
        raise NotImplementedError
        
    def getFollowers(self, userId):
        raise NotImplementedError
        
    def approveFriendship(self, friendship):
        raise NotImplementedError
    
    def addBlock(self, friendship):
        raise NotImplementedError
    
    def checkBlock(self, friendship):
        raise NotImplementedError
            
    def removeBlock(self, friendship):
        raise NotImplementedError
            
    def getBlocks(self, userId):
        raise NotImplementedError
    