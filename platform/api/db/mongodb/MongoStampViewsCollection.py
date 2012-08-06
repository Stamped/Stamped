#!/usr/bin/env python
from __future__ import absolute_import

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from api.db.mongodb.AMongoCollection import AMongoCollection

class MongoStampViewsCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='stampviews')
    
    ### PUBLIC
    
    def addStampView(self, stampId, userId):
        self._createRelationship(keyId=stampId, refId=userId)
        return True
            
    def removeStampView(self, stampId, userId):
        return self._removeRelationship(keyId=stampId, refId=userId)
            
    def getStampViews(self, stampId, limit=None):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(stampId, limit)

