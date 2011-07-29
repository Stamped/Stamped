#!/usr/bin/python

__author__ = "Stamped (dev@Stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from Activity import Activity
from utils import abstract

class AActivityDB(object):
    
    """
    Activity is created for User in the following scenarios:
    
    * User is given credit (restamp)
    * Someone comments on a stamp User is mentioned in
    * Someone "favorites" User's stamp
    * Someone directs a stamp to User (with optional comment)
    * User achieves milestone
    
    Mentions:
    * User is mentioned in a comment
    * User is mentioned in a stamp
    
    Comments:
    * User is mentioned in a comment -> Mentions
    * User comments on a stamp
    * Someone comments on User's stamp
    * Someone replies to User's comment
    """
    
    @abstract
    def addActivity(self, recipientId, activity):
        pass
    
    @abstract    
    def addActivityForRestamp(self, recipientIds, user, stamp):
        pass
    
    @abstract    
    def addActivityForComment(self, recipientIds, user, stamp, comment):
        pass
    
    @abstract    
    def addActivityForReply(self, recipientIds, user, stamp, comment):
        pass
    
    @abstract    
    def addActivityForFavorite(self, recipientIds, user, stamp):
        pass
    
    @abstract    
    def addActivityForDirected(self, recipientIds, user, stamp):
        pass
    
    @abstract  
    def addActivityForMention(self, recipientIds, user, stamp, comment=None):
        pass
    
    @abstract    
    def addActivityForMilestone(self, recipientId, activity):
        pass
    
    @abstract
    def getActivity(self, userId, before=None, since=None, limit=None):
        pass
    
    @abstract
    def removeActivity(self, activityId):
        pass

