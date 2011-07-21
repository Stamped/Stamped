#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from abc import abstractmethod
from Friendship import Friendship

class AFriendshipDB(object):
    
    def __init__(self, desc):
        self._desc = desc
    
    def addFriendship(self, friendship):
        pass
        
    @abstractmethod
    def checkFriendship(self, friendship):
        pass
        
    @abstractmethod
    def removeFriendship(self, friendship):
        pass
        
    @abstractmethod
    def getFriends(self, userId):
        pass
        
    @abstractmethod
    def getFollowers(self, userId):
        pass
        
    @abstractmethod
    def approveFriendship(self, friendship):
        pass
        
    @abstractmethod
    def addBlock(self, friendship):
        pass
        
    @abstractmethod
    def checkBlock(self, friendship):
        pass
        
    @abstractmethod
    def removeBlock(self, friendship):
        pass
        
    @abstractmethod
    def getBlocks(self, userId):
        pass
        
    
