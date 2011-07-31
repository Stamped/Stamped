#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals

from datetime import datetime
from utils import lazyProperty

from AMongoCollection import AMongoCollection
from MongoStampCommentsCollection import MongoStampCommentsCollection

from api.ACommentDB import ACommentDB
from api.Comment import Comment

class MongoCommentCollection(AMongoCollection, ACommentDB):
        
    SCHEMA = {
        '_id': object,
        'stamp_id': basestring,
        'user': {
            'user_id': basestring,
            'screen_name': basestring,
            'display_name': basestring,
            'profile_image': basestring,
            'color_primary': basestring,
            'color_secondary': basestring,
            'privacy': bool
        },
        'restamp_id': basestring,
        'blurb': basestring,
        'mentions': [],
        'timestamp': {
            'created': datetime
        }
    }
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='comments')
        ACommentDB.__init__(self)
    
    ### PUBLIC
    
    @lazyProperty
    def stamp_comments_collection(self):
        return MongoStampCommentsCollection()
    
    def addComment(self, comment):
        ### TODO: Make sure that the user can publish comment (public stamp and not blocked)
        commentId = self._addDocument(comment, 'comment_id')
        self.stamp_comments_collection.addStampComment(comment['stamp_id'], commentId)
        ### TODO: Add to activity feed
        return commentId
    
    def getComment(self, commentId):
        comment = Comment(self._getDocumentFromId(commentId, 'comment_id'))
        if comment.isValid == False:
            raise KeyError("Comment not valid")
        return comment
        
    def removeComment(self, commentID):
        self._removeDocument(commentID)
        return True
    
    # Can comments be updated? If a comment then *no*, but if it's a restamp 
    # then *maybe*. Discuss on product side before implementing here.
    
    def getCommentIds(self, stampId):
        return self.stamp_comments_collection.getStampCommentIds(stampId)
        
    def getNumberOfComments(self, stampId):
        return len(self.getCommentIds(stampId))
    
    def getComments(self, stampId):
        comments = self._getDocumentsFromIds(self.getCommentIds(stampId), 'comment_id')
        result = []
        for comment in comments:
            comment = Comment(comment)
            if comment.isValid == False:
                raise KeyError("Comment not valid")
            result.append(comment)
        return result
    
    def getCommentsAcrossStamps(self, stampIds):
        commentIds = self.stamp_comments_collection.getCommentIdsAcrossStampIds(stampIds)
        comments = self._getDocumentsFromIds(commentIds, 'comment_id', limit=len(commentIds))
        result = []
        for comment in comments:
            comment = Comment(comment)
            if comment.isValid == False:
                raise KeyError("Comment not valid")
            result.append(comment)
        return result

