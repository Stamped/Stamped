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
        AMongoCollection.__init__(self, collection='entities')
        AEntityDB.__init__(self)

    @lazyProperty
    def places_collection(self):
        return MongoPlacesEntityCollection()
    
    def _convertToMongo(self, entity):
        document = entity.exportSparse()
        if 'entity_id' in document:
            document['_id'] = self._getObjectIdFromString(document['entity_id'])
            del(document['entity_id'])
        return document

    def _convertFromMongo(self, document):
        if '_id' in document:
            document['entity_id'] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])
        return Entity(document)
    
    ### PUBLIC
    
    def addEntity(self, entity):
        document = self._convertToMongo(entity)
        document = self._addMongoDocument(document)
        entity = self._convertFromMongo(document)

        if entity.coordinates.lat != None:
            self.places_collection.addEntity(entity.exportSchema(EntityPlace()).value)

        return entity
    
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
        return self._addDocuments(entities, 'entity_id')
    
    def searchEntities(self, input_query, limit=20):
        input_query = input_query.lower()
        query = input_query
        query = query.strip()
        query = query.replace(']', '\]?')
        query = query.replace('(', '\(')
        query = query.replace(')', '\)')
        query = query.replace('|', '\|')
        query = query.replace(' and ', ' (and|&)? ')
        query = query.replace('.', '\.?')
        query = query.replace('&', ' & ')
        query = query.replace('-', '-?')
        query = query.replace(' ', '[ \t-_]*')
        query = query.replace("'", "'?")
        
        results = []
        hard_limit = 100
        db_results = self._collection.find({"title": {"$regex": query, "$options": "i"}}).limit(hard_limit)
        
        for result in db_results:
            entity = Entity(self._mongoToObj(result, 'entity_id'))
            results.append(entity)
        
        if len(results) > 1:
            is_junk = " \t-".__contains__
            #lambda x: x in " \t-"
            
            for i in xrange(len(results)):
                entity = results[i]
                ratio  = 1.0 - SequenceMatcher(is_junk, input_query, entity.title.lower()).ratio()
                subcategory_index = subcategory_indices[entity.subcategory]
                
                results[i] = (ratio, subcategory_index, entity)
            
            results = sorted(results)
            results = results[0:min(len(results), limit)]
            results = map(lambda r: r[2], results)
        
        return results

