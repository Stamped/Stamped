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
        
    """
    Activity is created for User in the following scenarios:
    
    * User is given credit (restamp)
    * User is mentioned in a stamp
    * User is mentioned in a comment
    * User comments on a stamp
    * Someone replies to User's comment
    * Someone comments on a stamp User is mentioned in
    * Someone comments on User's stamp
    * Someone "favorites" User's stamp
    * Someone directs a stamp to User (with optional comment)
    * User achieves milestone
    
    """

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
        
