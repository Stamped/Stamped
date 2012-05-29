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

class MongoGuideCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='guides', primary_key='user_id', obj=GuideCache)
    
    ### PUBLIC
    
    def addGuide(self, guide):
        return self._addObject(guide)
    
    def removeGuide(self, userId):
        documentId = self._getObjectIdFromString(userId)
        return self._removeMongoDocument(documentId)
    
    def getGuide(self, userId):
        documentId = self._getObjectIdFromString(userId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)

    def updateGuide(self, guide):
        return self.update(guide)

