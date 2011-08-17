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
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='comments')
        ACommentDB.__init__(self)
    
    def _convertToMongo(self, comment):
        document = comment.exportSparse()
        if 'comment_id' in document:
            document['_id'] = self._getObjectIdFromString(document['comment_id'])
            del(document['comment_id'])
        return document

    def _convertFromMongo(self, document):
        if '_id' in document:
            document['comment_id'] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])
        return Comment(document)
    
    ### PUBLIC

    @lazyProperty
    def stamp_comments_collection(self):
        return MongoStampCommentsCollection()
    
    def addComment(self, comment):
        document = self._convertToMongo(comment)
        document = self._addMongoDocument(document)
        comment = self._convertFromMongo(document)

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
    
    def getCommentIds(self, stampId):
        return self.stamp_comments_collection.getStampCommentIds(stampId)
    
    def getComments(self, stampId):
        documentIds = []
        for documentId in self.getCommentIds(stampId):
            documentIds.append(self._getObjectIdFromString(documentId))
        comments = []
        for document in self._getMongoDocumentsFromIds(documentIds):
            comments.append(self._convertFromMongo(document))
        return comments
    
    def getCommentsAcrossStamps(self, stampIds, limit=4):
        commentIds = self.stamp_comments_collection.getCommentIdsAcrossStampIds(stampIds, limit)


        documentIds = []
        for commentId in commentIds:
            documentIds.append(self._getObjectIdFromString(commentId))

        # Get comments
        documents = self._getMongoDocumentsFromIds(documentIds, limit=len(commentIds))

        comments = []
        for document in documents:
            comments.append(self._convertFromMongo(document))

        return comments





        
    def getNumberOfComments(self, stampId):
        return len(self.getCommentIds(stampId))