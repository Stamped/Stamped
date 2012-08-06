#!/usr/bin/env python
from __future__ import absolute_import

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals
from api.db.mongodb.AMongoCollection import AMongoCollection

class MongoCreditGiversCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='creditgivers')
    
    ### PUBLIC
    
    def addGiver(self, userId, giverId):
        self._createRelationship(keyId=userId, refId=giverId)
        return self.numGivers(userId)
    
    def removeGiver(self, userId, giverId):
        return self._removeRelationship(keyId=userId, refId=giverId)
            
    def getGivers(self, userId):
        return self._getRelationships(userId)
        
    def numGivers(self, userId):
        return len(self.getGivers(userId))

