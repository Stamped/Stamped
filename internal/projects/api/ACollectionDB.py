#!/usr/bin/python

__author__ = "Stamped (dev@Stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from Collection import Collection

class ACollectionDB(object):
    
    def __init__(self, desc):
        self._desc = desc
    
    def getInbox(self, userID):
        raise NotImplementedError
    
    def getUser(self, userID):
        raise NotImplementedError
    
    def getFavorites(self, userID):
        raise NotImplementedError
    
    def getMentions(self, userID):
        raise NotImplementedError
    
    def __len__(self):
        raise NotImplementedError
    
    def __str__(self):
        return self._desc

