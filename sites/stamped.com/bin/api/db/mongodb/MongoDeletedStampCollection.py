#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, logs, re

from datetime import datetime
from utils import lazyProperty

from Schemas import *

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
        return self._addObject(stamp)
    
    def getStamp(self, stampId):
        documentId = self._getObjectIdFromString(stampId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)
    
    def removeStamp(self, stampId):
        documentId = self._getObjectIdFromString(stampId)
        return self._removeMongoDocument(documentId)

    def getStamps(self, stampIds, **kwargs):
        params = {
            'since':    kwargs.pop('since', None),
            'before':   kwargs.pop('before', None), 
            'limit':    kwargs.pop('limit', 20),
            'sort':     'timestamp.modified',
        }

        documentIds = []
        for stampId in stampIds:
            documentIds.append(self._getObjectIdFromString(stampId))

        # Get stamps
        documents = self._getMongoDocumentsFromIds(documentIds, **params)

        stamps = []
        for document in documents:
            stamp = self._convertFromMongo(document)
            stamp.deleted = True
            stamps.append(stamp)

        return stamps
