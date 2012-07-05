#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from api.Schemas import *

from api.db.mongodb.AMongoCollection import AMongoCollection
from api.APlacesEntityDB import APlacesEntityDB
from api.Entity import buildEntity

class MongoPlacesEntityCollection(AMongoCollection, APlacesEntityDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='places', primary_key='entity_id', obj=BasicEntity)
        APlacesEntityDB.__init__(self)
    
    ### TODO: Rework this (hacking it right now)
    
    def _convertFromMongo(self, document):
        if document is None:
            return None

        if 'coordinates' in document:
            document['coordinates'] = {
                'lat': document['coordinates'][1],
                'lng': document['coordinates'][0],
            }

        if '_id' in document and self._primary_key is not None:
            document[self._primary_key] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])
            
        document.pop('titlel')

        entity = buildEntity(document)
        
        return entity
    
    def _convertToMongo(self, entity):
        if entity.entity_id is not None and entity.entity_id.startswith('T_'):
            del entity.entity_id
        document = AMongoCollection._convertToMongo(self, entity)
        if document is None:
            return None
        if 'title' in document:
            document['titlel'] = getSimplifiedTitle(document['title'])
        if 'coordinates' in document:
            document['coordinates'] = [
                document['coordinates']['lng'], 
                document['coordinates']['lat'], 
            ]
        return document
    
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

