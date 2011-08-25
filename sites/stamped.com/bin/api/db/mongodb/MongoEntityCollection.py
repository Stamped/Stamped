#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals

from datetime import datetime
from utils import lazyProperty

from Schemas import *

from AMongoCollection import AMongoCollection
from MongoPlacesEntityCollection import MongoPlacesEntityCollection
from AEntityDB import AEntityDB
from difflib import SequenceMatcher

subcategory_indices = {
    'restaurant' : 0, 
    'bar' : 0, 
    'book' : 3, 
    'movie' : 2, 
    'artist' : 1, 
    'song' : 8, 
    'album' : 7, 
    'app' : 9, 
    'other' : 10,
}

class MongoEntityCollection(AMongoCollection, AEntityDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='entities', primary_key='entity_id', obj=Entity)
        AEntityDB.__init__(self)
    
    @lazyProperty
    def places_collection(self):
        return MongoPlacesEntityCollection()
    
    ### PUBLIC
    
    def addEntity(self, entity):
        return self._addObject(entity)
    
    def getEntity(self, entityId):
        documentId = self._getObjectIdFromString(entityId)
        document   = self._getMongoDocumentFromId(documentId)
        
        return self._convertFromMongo(document)
    
    def updateEntity(self, entity):
        document = self._convertToMongo(entity)
        document = self._updateMongoDocument(document)
        
        return self._convertFromMongo(document)
    
    def removeEntity(self, entityId):
        documentId = self._getObjectIdFromString(entityId)
        return self._removeMongoDocument(documentId)
    
    def removeCustomEntity(self, entityId, userId):
        try:
            query = {'_id': self._getObjectIdFromString(entityId), \
                        'sources.userGenerated.user_id': userId}
            self._collection.remove(query)
            return True
        except:
            logs.warning("Cannot remove document")
            raise Exception
    
    def addEntities(self, entities):
        return self._addObjects(entities)

