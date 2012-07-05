#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from api.db.mongodb.AMongoCollection import AMongoCollection

class MongoStampCommentsCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='stampcomments')
    
    ### PUBLIC
    
    def addStampComment(self, stampId, commentId):
        self._createRelationship(keyId=stampId, refId=commentId)
        return True
        
    def addStampComments(self, stampIds, commentId):
        for stampId in stampIds:
            self.addStampComment(stampId, commentId)
        return True
            
    def removeStampComment(self, stampId, commentId):
        return self._removeRelationship(keyId=stampId, refId=commentId)
            
    def getStampCommentIds(self, stampId, limit=None):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(stampId, limit)
        
    def getCommentIdsAcrossStampIds(self, stampIds, limit=0):
        return self._getRelationshipsAcrossKeys(stampIds, limit)

