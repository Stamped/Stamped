#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from User import User

class AUserDB(object):
    
    def __init__(self, desc):
        self._desc = desc
    
    def addUser(self, user):
        raise NotImplementedError
    
    def getUser(self, userID):
        raise NotImplementedError
    
    def updateUser(self, user):
        raise NotImplementedError
    
    def removeUser(self, userID):
        raise NotImplementedError
        
    def flagUser(self, userID, flag=1):
        raise NotImplementedError
        
    def lookupUsers(self, userIDs, usernames):
        # Must set userIDs or usernames to 'None' if not using
        raise NotImplementedError
        
    def searchUsers(self, searchQuery):
        raise NotImplementedError
        
    
    def addUsers(self, users):
        return map(self.addUser, users)
    
    def getUsers(self, userIDs):
        return map(self.getUser, userIDs)
    
    def updateUsers(self, users):
        return map(self.updateUser, users)
    
    def removeUsers(self, userIDs):
        return map(self.removeUser, userIDs)
        
    def flagUsers(self, userIDs, flag=1):
        return map(self.flagUser, userIDs, flag)
    
    def __len__(self):
        raise NotImplementedError
    
    def __str__(self):
        return self._desc

