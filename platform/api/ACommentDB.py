#!/usr/bin/env python

__author__    = "Stamped (dev@Stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import abstract

class ACommentDB(object):
    
    @abstract
    def addComment(self, comment):
        pass
        
    @abstract
    def getComment(self, commentId):
        pass
        
    @abstract
    def removeComment(self, comment):  
        pass
        
    @abstract
    def getCommentIds(self, stampId):
        pass
        
    @abstract    
    def getComments(self, stampId):
        pass
    
    @abstract  
    def getCommentsAcrossStamps(self, stampIds, limit=4):
        pass
