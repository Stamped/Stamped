#!/usr/bin/python

__author__ = "Stamped (dev@Stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from Comment import Comment

class ACommentDB(object):
    
    def __init__(self, desc):
        self._desc = desc
    
    def addComment(self, comment):
        raise NotImplementedError
    
    def getComment(self, commentID):
        raise NotImplementedError
        
    def getConversation(self, stampID):
        raise NotImplementedError
    
    def removeComment(self, commentID):
        raise NotImplementedError
        
    def removeConversation(self, stampID):
        raise NotImplementedError
    
    def addComments(self, comments):
        return map(self.addComment, comments)
    
    def getComments(self, commentIDs):
        return map(self.getComment, commentIDs)
    
    def removeComments(self, commentIDs):
        return map(self.removeComment, commentIDs)
    
    def __len__(self):
        raise NotImplementedError
    
    def __str__(self):
        return self._desc

