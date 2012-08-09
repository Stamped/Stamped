#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

import logs
from utils import lazyProperty

from db.mongodb.MongoCommentCollection import MongoCommentCollection
from db.mongodb.MongoStampCommentsCollection import MongoStampCommentsCollection

class CommentDB(object):

    @lazyProperty
    def __comment_collection(self):
        return MongoCommentCollection()

    @lazyProperty
    def __stamp_comments_collection(self):
        return MongoStampCommentsCollection()
    
    def addComment(self, comment):
        return self.__comment_collection.addComment(comment)
    
    def removeComment(self, commentId):
        return self.__comment_collection.removeComment(comment)
    
    def getComment(self, commentId):
        return self.__comment_collection.getComment(commentId)
    
    def getComments(self, commentIds):
        return self.__comment_collection.getComments(commentIds)
    
    def getCommentIds(self, stampId):
        return self.__stamp_comments_collection.getStampCommentIds(stampId)
    
    def getCommentsForStamp(self, stampId, **kwargs):
        return self.__comment_collection.getCommentsForStamp(stampId, **kwargs)
    
    def getCommentsAcrossStamps(self, stampIds, limit=4):
        return self.__comment_collection.getCommentsAcrossStamps(stampIds, limit=limit)

    def getUserCommentIds(self, userId):
        return self.__comment_collection.getUserCommentIds(userId)

