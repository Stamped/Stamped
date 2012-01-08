#!/usr/bin/python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2012 Stamped.com'
__license__   = 'TODO'

import Globals

from AMongoCollection import AMongoCollection

class MongoUserActivityCollection(AMongoCollection):
    
    SCHEMA = {
        '_id': basestring,
        'activity_id': basestring
    }
    
    def __init__(self, setup=False):
        AMongoCollection.__init__(self, collection='useractivity')
    
    ### PUBLIC
    
    def addUserActivity(self, userId, activityId):
        if not isinstance(userId, basestring) or not isinstance(activityId, basestring):
            raise KeyError("ID not valid")
        
        self._createRelationship(keyId=userId, refId=activityId)
        return True
            
    def removeUserActivity(self, userId, activityId):
        return self._removeRelationship(keyId=userId, refId=activityId)
            
    def getUserActivityIds(self, userId):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(userId)

