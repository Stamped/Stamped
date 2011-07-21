#!/usr/bin/python

__author__ = "Stamped (dev@Stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from abc import abstractmethod
from Comment import Comment

class ACommentDB(object):
    
    def __init__(self, desc):
        self._desc = desc

    @abstractmethod
    def addComment(self, comment):
        pass
        
    @abstractmethod
    def getComment(self, commentId):
        pass
        
    @abstractmethod
    def removeComment(self, comment):  
        pass
        
    @abstractmethod
    def getCommentIds(self, stampId):
        pass
        
    @abstractmethod    
    def getComments(self, stampId):
        pass
        
