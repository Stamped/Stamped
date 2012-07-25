#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, logs, time, pymongo

from datetime import datetime
from utils import lazyProperty
from api.Schemas import *

from api.db.mongodb.AMongoCollection import AMongoCollection
from api.db.mongodb.MongoStampCommentsCollection import MongoStampCommentsCollection

from api.ACommentDB import ACommentDB

from libs.Memcache                              import globalMemcache

class MongoCommentCollection(AMongoCollection, ACommentDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='comments', primary_key='comment_id', obj=Comment, overflow=True)
        ACommentDB.__init__(self)

        self._collection.ensure_index('user.user_id')
        self._collection.ensure_index('timestamp.created')
        self._collection.ensure_index([('stamp_id', pymongo.ASCENDING)])
        self._collection.ensure_index([('_id', pymongo.ASCENDING), ('timestamp.created',pymongo.DESCENDING)])

        self._cache = globalMemcache()


    ### CACHING

    def _getCachedComment(self, commentId):
        key = str("obj::comment::%s" % commentId)
        return self._cache[key]

    def _setCachedComment(self, comment):
        key = str("obj::comment::%s" % comment.comment_id)
        cacheLength = 60 * 10 # 10 minutes
        try:
            self._cache.set(key, comment, time=cacheLength)
        except Exception as e:
            logs.warning("Unable to set cache for %s: %s" % (comment.comment_id, e))

    def _delCachedComment(self, commentId):
        key = str("obj::comment::%s" % commentId)
        try:
            del(self._cache[key])
        except KeyError:
            pass

    
    ### PUBLIC

    @lazyProperty
    def stamp_comments_collection(self):
        return MongoStampCommentsCollection()
    
    def addComment(self, comment):
        comment = self._addObject(comment)
        self.stamp_comments_collection.addStampComment(comment.stamp_id, comment.comment_id)
        self._setCachedComment(comment)

        return comment
    
    def removeComment(self, commentId):
        documentId = self._getObjectIdFromString(commentId)

        comment = self.getComment(documentId)
        self.stamp_comments_collection.removeStampComment(comment.stamp_id, comment.comment_id)
        self._delCachedComment(commentId)

        return self._removeMongoDocument(documentId)
    
    def getComment(self, commentId):
        try:
            return self._getCachedComment(commentId)
        except KeyError:
            pass

        documentId = self._getObjectIdFromString(commentId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)
    
    def getComments(self, commentIds):
        result = []

        documentIds = []
        for commentId in commentIds:
            try:
                result.append(self._getCachedComment(commentId))
            except KeyError:
                documentIds.append(self._getObjectIdFromString(commentId))
        documents = self._getMongoDocumentsFromIds(documentIds)

        for document in documents:
            comment = self._convertFromMongo(document)
            self._setCachedComment(comment)
            result.append(comment)

        return result
    
    def getCommentIds(self, stampId):
        return self.stamp_comments_collection.getStampCommentIds(stampId)
    
    def getCommentsForStamp(self, stampId, **kwargs):
        before  = kwargs.pop('before', None)
        limit   = kwargs.pop('limit', 0)
        offset  = kwargs.pop('offset', 0)
        
        ### TODO: Add paging
        documentIds = []
        for documentId in self.getCommentIds(stampId):
            documentIds.append(self._getObjectIdFromString(documentId))

        # Short circuit if no comments
        if len(documentIds) == 0:
            return []

        query = { '_id': { '$in': documentIds } }
        if before is not None:
            query['timestamp.created'] = { '$lte': before }

        if limit == 0 and offset > 0:
            queryLimit = 0
        elif limit < 0 or offset < 0:
            queryLimit = 0
        else:
            queryLimit = limit + offset

        comments = []
        documents = self._collection.find(query).sort('timestamp.created', pymongo.DESCENDING).limit(queryLimit)

        for document in documents:
            comments.append(self._convertFromMongo(document))
        return comments[offset:]
    
    def getCommentsAcrossStamps(self, stampIds, limit=4):
        commentIds = self.stamp_comments_collection.getCommentIdsAcrossStampIds(stampIds, limit)

        documentIds = []
        for commentId in commentIds:
            documentIds.append(self._getObjectIdFromString(commentId))

        # Short circuit if no comments
        if len(documentIds) == 0:
            return []
        
        # Get comments
        documents = self._getMongoDocumentsFromIds(documentIds, limit=len(documentIds))
        
        comments = []
        for document in documents:
            comments.append(self._convertFromMongo(document))
        
        return comments

    def getUserCommentIds(self, userId):
        documents = self._collection.find({'user.user_id': userId})

        comments = []
        for document in documents:
            comments.append(self._convertFromMongo(document))
        
        return comments
        
