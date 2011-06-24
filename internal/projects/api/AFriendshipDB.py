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
    
    def removeFriendship(self, userID, followingID):
        raise NotImplementedError
    
    def checkFriendship(self, userID, followingID):
        raise NotImplementedError
    
    def getFriendship(self, userID, followingID):
        raise NotImplementedError
    
    def addFriendships(self, friendships):
        return map(self.addFriendship, friendships)
    
    def getFriendships(self, friendships):
        return map(self.getFriendship, friendships)
    
    def checkFriendships(self, friendships):
        return map(self.checkFriendship, friendships)
    
    def removeFriendships(self, friendships):
        return map(self.removeFriendship, friendships)
    
    def __len__(self):
        raise NotImplementedError
    
    def __str__(self):
        return self._desc

