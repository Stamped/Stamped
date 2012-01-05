#!/usr/bin/python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2012 Stamped.com'
__license__   = 'TODO'

import Globals

from AMongoCollection import AMongoCollection

class MongoUserFavEntitiesCollection(AMongoCollection):
    
    SCHEMA = {
        '_id': basestring,
        'entity_id': basestring
    }
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='userfaventities')
    
    ### PUBLIC
    
    def addUserFavoriteEntity(self, userId, entityId):
        self._createRelationship(keyId=userId, refId=entityId)
        return True
    
    def removeUserFavoriteEntity(self, userId, entityId):
        return self._removeRelationship(keyId=userId, refId=entityId)
    
    def getUserFavoriteEntities(self, userId):
        ### TODO: Add limit? Add timestamp to slice?
        return self._getRelationships(userId)

