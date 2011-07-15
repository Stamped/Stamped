#!/usr/bin/python

__author__ = "Stamped (dev@Stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped, Inc."
__license__ = "TODO"

from abc import abstractmethod
from Collection import Collection

class ACollectionDB(object):
    
    def __init__(self, desc):
        self._desc = desc
    
    @abstractmethod
    def getInboxStampIDs(self, userId, limit=None):
        pass
        
    @abstractmethod
    def getInboxStamps(self, userId, limit=None):
        pass
        
    @abstractmethod
    def getUserStampIDs(self, userId, limit=None):
        pass
        
    @abstractmethod
    def getUserStamps(self, userId, limit=None):
        pass
        
    @abstractmethod
    def getMentions(self, userId, limit=None):
        pass
    