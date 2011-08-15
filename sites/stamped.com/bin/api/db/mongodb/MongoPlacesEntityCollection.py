#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils

from AMongoCollection import AMongoCollection
from utils import OrderedDict
from api.APlacesEntityDB import APlacesEntityDB
from api.Entity import Entity

class MongoPlacesEntityCollection(AMongoCollection, APlacesEntityDB):
    
    SCHEMA = {
        '_id': object, 
        'coordinates': {
            'lng' : float, 
            'lat' : float, 
        }, 
    }
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='places')
        APlacesEntityDB.__init__(self)
    

    ### TODO: Rework this (hacking it right now)

    def _convertToMongo(self, entity):
        document = entity
        if 'entity_id' in document:
            document['_id'] = self._getObjectIdFromString(document['entity_id'])
            del(document['entity_id'])
        return document

    def _convertFromMongo(self, document):
        if '_id' in document:
            document['entity_id'] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])
        return document
    
    ### PUBLIC
    
    def addEntity(self, entity):
        document = self._convertToMongo(entity)
        document = self._addMongoDocument(document)
        entity = self._convertFromMongo(document)

        return entity
    
    # def addEntity(self, entity):
    #     return self._addDocument(entity, 'entity_id')
    
    def getEntity(self, entityId):
        entity = Entity(self._getDocumentFromId(entityId, 'entity_id'))
        return entity
    
    def updateEntity(self, entity):
        return self._updateDocument(entity, 'entity_id')
    
    def removeEntity(self, entityID):
        return self._removeDocument(entityID)
    
    def addEntities(self, entities):
        return self._addDocuments(entities, 'entity_id')

