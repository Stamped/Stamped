#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils

from Schemas import *

from AMongoCollection import AMongoCollection
from utils import OrderedDict
from api.APlacesEntityDB import APlacesEntityDB


class MongoPlacesEntityCollection(AMongoCollection, APlacesEntityDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='places')
        APlacesEntityDB.__init__(self)
    

    ### TODO: Rework this (hacking it right now)

    def _convertToMongo(self, entity):
        document = entity.exportSparse()
        if 'entity_id' in document:
            document['_id'] = self._getObjectIdFromString(document['entity_id'])
            del(document['entity_id'])
        if 'coordinates' in document:
            document['coordinates'] = [
                document['coordinates']['lat'],
                document['coordinates']['lng']
            ]
        return document

    def _convertFromMongo(self, document):
        if '_id' in document:
            document['entity_id'] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])
        if 'coordinates' in document:
            document['coordinates'] = {
                'lat': document['coordinates'][0],
                'lng': document['coordinates'][1],
            }
        return Entity(document)
    
    ### PUBLIC
    
    def addEntity(self, entity):
        document = self._convertToMongo(entity)
        document = self._addMongoDocument(document)
        entity = self._convertFromMongo(document)

        return entity
    
    # def addEntity(self, entity):
    #     return self._addDocument(entity, 'entity_id')
    
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
        ### HACK 
        ### TODO: Make this better
        result = []
        for entity in entities:
            result.append(self.addEntity(entity))
        return result
    
    def _mongoToObj(self, data, objId='id'):
        data = AMongoCollection._mongoToObj(self, data, objId)
        coords = data['coordinates']
        data['coordinates'] = {
            'lat' : coords[1], 
            'lng' : coords[0], 
        }
        return data
    
    def _mapDataToSchema(self, data, schema):
        coords = data['coordinates']
        data['coordinates'] = [ coords['lng'], coords['lat'] ]
        return AMongoCollection._mapDataToSchema(self, data, schema)

