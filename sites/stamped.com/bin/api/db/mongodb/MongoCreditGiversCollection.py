#!/usr/bin/python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__   = 'TODO'

import Globals
from AMongoCollection import AMongoCollection

class MongoCreditGiversCollection(AMongoCollection):
    
    SCHEMA = {
        '_id': basestring,
        'user_id': basestring
    }
    
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

