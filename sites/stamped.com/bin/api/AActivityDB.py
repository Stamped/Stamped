#!/usr/bin/python

__author__ = "Stamped (dev@Stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from abc import abstractmethod
from Activity import Activity

class AActivityDB(object):
    
    def __init__(self, desc):
        self._desc = desc

    @abstractmethod    
    def addActivity(self, recipientId, activity):
        pass

    @abstractmethod    
    def addActivityForRestamp(self, recipientIds, user, stamp):
        pass

    @abstractmethod    
    def addActivityForComment(self, recipientIds, user, comment, stamp):
        pass

    @abstractmethod    
    def addActivityForFavorite(self, recipientIds, user, stamp):
        pass

    @abstractmethod    
    def addActivityForDirected(self, recipientIds, user, stamp):
        pass
        
    @abstractmethod  
    def addActivityForMention(self, recipientIds, user, stamp):
        pass

    @abstractmethod    
    def addActivityForMilestone(self, recipientId, activity):
        pass

        
    @abstractmethod
    def getActivity(self, userId, before=None, since=None, limit=None):
        pass
        
    @abstractmethod
    def removeActivity(self, activityId):
        pass
        
