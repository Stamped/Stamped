#!/usr/bin/env python

__author__    = "Stamped (dev@Stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract

class AActivityDB(object):
    
    """
    Activity is created for User in the following scenarios:
    
    * User is given credit (restamp)
    * Someone comments on a stamp User is mentioned in
    * Someone "todos" User's stamp
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
    def getActivity(self, userId, **kwargs):
        pass
    
    @abstract
    def addActivity(self, recipientIds, activity):
        pass
    
    @abstract
    def removeActivity(self, userId, activityId):
        pass

