#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from threading import Lock
from datetime import datetime

from api.ACommentDB import ACommentDB
from api.Comment import Comment
from MongoDB import Mongo
from MongoStampComments import MongoStampComments

class MongoComment(ACommentDB, Mongo):
        
    COLLECTION = 'comments'
        
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
    
    def __init__(self, setup=False):
        ACommentDB.__init__(self, self.DESC)
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def addComment(self, comment):
        ### TODO: Make sure that the user can publish comment (public stamp and not blocked)
        commentId = self._addDocument(comment, 'comment_id')
        MongoStampComments().addStampComment(comment['stamp_id'], commentId)
        ### TODO: Add to activity feed
        return commentId
    
    def getComment(self, commentId):
        comment = Comment(self._getDocumentFromId(commentId, 'comment_id'))
        if comment.isValid == False:
            raise KeyError("Comment not valid")
        return comment
        
    def removeComment(self, commentID):
        return self._removeDocument(commentID)
        
    
    # Can comments be updated? If a comment then *no*, but if it's a restamp 
    # then *maybe*. Discuss on product side before implementing here.
    
    def getCommentIds(self, stampId):
        return MongoStampComments().getStampCommentIds(stampId)
    
    def getComments(self, stampId):
        comments = self._getDocumentsFromIds(self.getCommentIds(stampId), 'comment_id')
        result = []
        for comment in comments:
            comment = Comment(comment)
            if comment.isValid == False:
                raise KeyError("Comment not valid")
            result.append(comment)
        return result
            
    
    ### PRIVATE
            
    
