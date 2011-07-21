#!/usr/bin/python

__author__ = 'Stamped (dev@stamped.com)'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__ = 'TODO'

import Globals
from threading import Lock
from datetime import datetime

from MongoDB import Mongo

class MongoCreditGivers(Mongo):
        
    COLLECTION = 'creditgivers'
        
    SCHEMA = {
        '_id': basestring,
        'user_id': basestring
    }
    
    def __init__(self, setup=False):
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
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


    ### PRIVATE
