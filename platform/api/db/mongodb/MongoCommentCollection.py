#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, logs, time

from datetime import datetime
from utils import lazyProperty
from api.Schemas import *

from AMongoCollection import AMongoCollection
from MongoStampCommentsCollection import MongoStampCommentsCollection

from api.ACommentDB import ACommentDB

class MongoCommentCollection(AMongoCollection, ACommentDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='comments', primary_key='comment_id', obj=Comment)
        ACommentDB.__init__(self)

        self._collection.ensure_index('user.user_id')
    
    ### PUBLIC

    @lazyProperty
    def stamp_comments_collection(self):
        return MongoStampCommentsCollection()
    
    def addComment(self, comment):
        comment = self._addObject(comment)
        self.stamp_comments_collection.addStampComment(comment.stamp_id, comment.comment_id)
        
        return comment
    
    def removeComment(self, commentId):
        documentId = self._getObjectIdFromString(commentId)

        comment = self.getComment(documentId)
        self.stamp_comments_collection.removeStampComment(comment.stamp_id, comment.comment_id)

        return self._removeMongoDocument(documentId)
    
    def getComment(self, commentId):
        documentId = self._getObjectIdFromString(commentId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)
    
    def getComments(self, commentIds):
        documentIds = map(self._getObjectIdFromString, commentIds)
        documents = self._getMongoDocumentsFromIds(documentIds)
        return map(self._convertFromMongo, documents)
    
    def getCommentIds(self, stampId):
        return self.stamp_comments_collection.getStampCommentIds(stampId)
    
    def getCommentsForStamp(self, stampId, limit=0):
        ### TODO: Add paging
        documentIds = []
        for documentId in self.getCommentIds(stampId):
            documentIds.append(self._getObjectIdFromString(documentId))
        comments = []
        for document in self._getMongoDocumentsFromIds(documentIds, limit=limit):
            comments.append(self._convertFromMongo(document))
        return comments
    
    def getCommentsAcrossStamps(self, stampIds, limit=4):
        commentIds = self.stamp_comments_collection.getCommentIdsAcrossStampIds(stampIds, limit)

        documentIds = []
        for commentId in commentIds:
            documentIds.append(self._getObjectIdFromString(commentId))

        if len(documentIds) == 0:
            return []
        
        # Get comments
        documents = self._getMongoDocumentsFromIds(documentIds, limit=len(documentIds))
        
        comments = []
        for document in documents:
            comments.append(self._convertFromMongo(document))
        
        return comments
    
    def getNumberOfComments(self, stampId):
        return len(self.getCommentIds(stampId))

    def getUserCommentIds(self, userId):
        documents = self._collection.find({'user.user_id': userId})

        comments = []
        for document in documents:
            comments.append(self._convertFromMongo(document))
        
        return comments
        
