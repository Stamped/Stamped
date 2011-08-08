#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals

from AMongoCollection import AMongoCollection
from api.APlacesEntityDB import APlacesEntityDB
from api.Entity import Entity

class MongoPlacesEntityCollection(AMongoCollection, APlacesEntityDB):
    
    SCHEMA = {
        '_id': basestring, 
        'title': basestring, 
        'subtitle': basestring,
        'desc': basestring, 
        'locale': basestring, 
        'category': basestring,
        'subcategory': basestring,
        'image': basestring, 
        'timestamp': {
            'created' : basestring, 
            'modified': basestring, 
        }, 
        'details': {
            'place': {
                'address': basestring, 
                'coordinates': {
                    'lng': float, 
                    'lat': float, 
                }, 
                'types': list, 
                'vicinity': basestring, 
                'neighborhood': basestring, 
                'crossStreet': basestring, 
                'publicTransit': basestring, 
                'parking': basestring, 
                'parkingDetails': basestring, 
                'wheelchairAccess': basestring, 
            }, 
            'contact': {
                'phone': basestring, 
                'fax': basestring, 
                'site': basestring, 
                'email': basestring, 
                'hoursOfOperation': basestring, 
            }, 
            'restaurant': {
                'diningStyle': basestring, 
                'cuisine': basestring, 
                'price': basestring, 
                'payment': basestring, 
                'dressCode': basestring, 
                'acceptsReservations': basestring, 
                'acceptsWalkins': basestring, 
                'offers': basestring, 
                'privatePartyFacilities': basestring, 
                'privatePartyContact': basestring, 
                'entertainment': basestring, 
                'specialEvents': basestring, 
                'catering': basestring, 
                'takeout': basestring, 
                'delivery': basestring, 
                'kosher': basestring, 
                'bar': basestring, 
                'alcohol': basestring, 
                'menuLink': basestring, 
                'chef': basestring, 
                'owner': basestring, 
                'reviewLinks': basestring, 
            }, 
        }, 
        'sources': {
            'googlePlaces': {
                'gid': basestring, 
                'gurl': basestring, 
                'reference': basestring, 
            }, 
            'openTable': {
                'rid': basestring, 
                'reserveURL': basestring, 
                'countryID': basestring, 
                'metroName': basestring, 
                'neighborhoodName': basestring, 
            }, 
            'factual': {
                'fid': basestring, 
                'table': basestring, 
            }, 
            'zagat' : {
                'zurl' : basestring, 
            }, 
            'urbanspoon' : {
                'uurl' : basestring, 
            }, 
            'nymag' : { }, 
        }
    }
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='places')
        APlacesEntityDB.__init__(self)
    
    ### PUBLIC
    
    def addEntity(self, entity):
        return self._addDocument(entity, 'entity_id')
    
    def getEntity(self, entityId):
        entity = Entity(self._getDocumentFromId(entityId, 'entity_id'))
        if entity.isValid == False:
            raise KeyError("Entity not valid")
        return entity
    
    def updateEntity(self, entity):
        return self._updateDocument(entity, 'entity_id')
    
    def removeEntity(self, entityID):
        return self._removeDocument(entityID)
    
    def addEntities(self, entities):
        return self._addDocuments(entities, 'entity_id')
    
    def matchEntities(self, query, limit=20):
        # Using a simple regex here. Need to rank results at some point...
        query = '^%s' % query
        result = []
        for entity in self._collection.find({"title": {"$regex": query, "$options": "i"}}).limit(limit):
            result.append(Entity(self._mongoToObj(entity, 'entity_id')))
        return result

