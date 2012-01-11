#!/usr/bin/python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals

from AMongoCollection import AMongoCollection

class MongoCreditReceivedCollection(AMongoCollection):
    
    SCHEMA = {
        '_id': basestring,
        'stamp_id': basestring
    }
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='creditreceived')
    
    ### PUBLIC
    
    def addCredit(self, userId, stampId):
        self._createRelationship(keyId=userId, refId=stampId)
        return self.numCredit(userId)
    
    def removeCredit(self, userId, stampId):
        return self._removeRelationship(keyId=userId, refId=stampId)
            
    def getCredit(self, userId):
        return self._getRelationships(userId)
        
    def numCredit(self, userId):
        return len(self.getCredit(userId))

