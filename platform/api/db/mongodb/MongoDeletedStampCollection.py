#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, logs, re

from datetime import datetime
from utils import lazyProperty

from api.Schemas import *

from AMongoCollection import AMongoCollection

from api.AStampDB import AStampDB

class MongoDeletedStampCollection(AMongoCollection, AStampDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='deletedstamps', primary_key='stamp_id', obj=DeletedStamp)
        AStampDB.__init__(self)

        self._collection.ensure_index('timestamp.modified', unique=False)
    
    ### PUBLIC
    
    def addStamp(self, stampId):
        d = datetime.utcnow()
        stamp = DeletedStamp()
        stamp.stamp_id = stampId
        stamp.timestamp.modified = d
        documentId = self._getObjectIdFromString(stampId)
        stamp.timestamp.created = documentId.generation_time.replace(tzinfo=None)
        return self._addObject(stamp)
    
    def getStamp(self, stampId):
        documentId = self._getObjectIdFromString(stampId)
        document = self._getMongoDocumentFromId(documentId)
        document['timestamp']['created'] = documentId.generation_time.replace(tzinfo=None)
        return self._convertFromMongo(document)
    
    def removeStamp(self, stampId):
        documentId = self._getObjectIdFromString(stampId)
        return self._removeMongoDocument(documentId)

    def getStamps(self, stampIds, genericCollectionSlice):
        # NOTE: only supports sorting by 'modified' and 'created'
        params = {
            'since':    genericCollectionSlice.since, 
            'before':   genericCollectionSlice.before, 
            'limit':    genericCollectionSlice.limit, 
            'sort':     "timestamp.%s" % genericCollectionSlice.sort, 
        }
        
        ids = map(self._getObjectIdFromString, stampIds)
        
        # Get stamps
        documents = self._getMongoDocumentsFromIds(ids, **params)
        
        stamps = []
        for document in documents:
            document['timestamp']['created'] = document['_id'].generation_time.replace(tzinfo=None)
            stamp = self._convertFromMongo(document)
            stamp.deleted = True
            stamps.append(stamp)
        
        return stamps

