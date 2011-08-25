#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils

from Schemas import *

from AMongoCollection import AMongoCollection
from api.APlacesEntityDB import APlacesEntityDB

class MongoPlacesEntityCollection(AMongoCollection, APlacesEntityDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='places', primary_key='entity_id', obj=Entity)
        APlacesEntityDB.__init__(self)
    
    ### TODO: Rework this (hacking it right now)
    
    def _convertToMongo(self, entity):
        document = AMongoCollection._convertToMongo(self, entity)
        
        if 'coordinates' in document:
            document['coordinates'] = [
                document['coordinates']['lng'], 
                document['coordinates']['lat'], 
            ]
        return document
    
    def _convertFromMongo(self, document):
        if 'coordinates' in document:
            document['coordinates'] = {
                'lat': document['coordinates'][1],
                'lng': document['coordinates'][0],
            }
        
        return AMongoCollection._convertFromMongo(self, document)
    
    ### PUBLIC
    
    def addEntity(self, entity):
        return self._addObject(entity)
    
    def getEntity(self, entityId):
        documentId = self._getObjectIdFromString(entityId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)
    
    def updateEntity(self, entity):
        document = self._convertToMongo(entity)
        document = self._updateMongoDocument(document)
        return self._convertFromMongo(document)
    
    def removeEntity(self, entityId):
        documentId = self._getObjectIdFromString(entityId)
        return self._removeMongoDocument(documentId)
    
    def addEntities(self, entities):
        return self._addObjects(entities)

