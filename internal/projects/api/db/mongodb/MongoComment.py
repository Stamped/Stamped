#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from threading import Lock
from datetime import datetime

from MongoDB import Mongo
from ACommentDB import ACommentDB
from Comment import Comment
from MongoStampComments import MongoStampComments

class MongoComment(ACommentDB, Mongo):
        
    COLLECTION = 'comments'
        
    SCHEMA = {
        '_id': object,
        'stamp_id': basestring,
        'user': {
            'user_id': basestring,
            'user_name': basestring,
            'user_img': basestring,
            'user_primary_color': basestring,
            'user_secondary_color': basestring
        },
        'restamp_id': basestring,
        'blurb': basestring,
        'mentions': [],
        'timestamp': basestring
    }
    
    def __init__(self, setup=False):
        ACommentDB.__init__(self, self.DESC)
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def addComment(self, comment):
        commentId = self._addDocument(comment)
        MongoStampComments().addStampComment(comment['stamp_id'], commentId)
        ### TODO: Add to activity feed
        return commentId
    
    def getComment(self, commentId):
        comment = Comment(self._getDocumentFromId(commentId))
        if comment.isValid == False:
            raise KeyError("Comment not valid")
        return comment
        
    def removeComment(self, comment):
        return self._removeDocument(comment)
        
#     def updateComment(self, commentId, complete=True):
#         if not isinstance(complete, bool):
#             raise TypeError("Not a bool!")
#         return self._validateUpdate(
#             self._collection.update(
#                 {'_id': self._getObjectIdFromString(favoriteId)}, 
#                 {'$set': {'complete': complete}},
#                 safe=True)
#             )
    
    def getCommentIds(self, stampId):
        return MongoStampComments().getStampCommentIds(stampId)
    
    def getComments(self, stampId):
        comments = self._getDocumentsFromIds(self.getCommentIds(stampId))
        result = []
        for comment in comments:
            comment = Comment(comment)
            if comment.isValid == False:
                raise KeyError("Comment not valid")
            result.append(comment)
        return result
            
    
    ### PRIVATE
            
    