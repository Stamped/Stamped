#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from api.db.mongodb.AMongoCollection import AMongoCollection

class MongoBlockCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='blocks')
    
    ### PUBLIC
    
    def addBlock(self, userId, friendId):
        self._createRelationship(keyId=userId, refId=friendId)
        return True
    
    def checkBlock(self, userId, friendId):
        return self._checkRelationship(keyId=userId, refId=friendId)
            
    def removeBlock(self, userId, friendId):
        return self._removeRelationship(keyId=userId, refId=friendId)
            
    def getBlocks(self, userId):
        return self._getRelationships(userId)

