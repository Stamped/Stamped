#!/usr/bin/python

__author__ = "Stamped (dev@Stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from Activity import Activity
from utils import abstract

class AActivityDB(object):
    
    @abstract    
    def addActivity(self, recipientId, activity):
        pass
    
    @abstract    
    def addActivityForRestamp(self, recipientIds, user, stamp):
        pass
    
    @abstract    
    def addActivityForComment(self, recipientIds, user, comment, stamp):
        pass
    
    @abstract    
    def addActivityForFavorite(self, recipientIds, user, stamp):
        pass
    
    @abstract    
    def addActivityForDirected(self, recipientIds, user, stamp):
        pass
    
    @abstract  
    def addActivityForMention(self, recipientIds, user, stamp):
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

