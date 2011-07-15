#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from threading import Lock
from datetime import datetime

from MongoDB import Mongo
from AEntityDB import AEntityDB
from Entity import Entity

class MongoEntity(AEntityDB, Mongo):
        
    COLLECTION = 'entities'
        
    SCHEMA = {
        '_id': object, 
        'title': basestring, 
        'desc': basestring, 
        'locale': basestring, 
        'category': basestring,
        'images': list, 
        'date': {
            'created' : basestring, 
            'modified': basestring, 
        }, 
        'details': {
            'place': {
                'address': basestring, 
                'coordinates': {
                    'lat': float, 
                    'lng': float
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
            'iPhoneApp': {
                'developer': basestring, 
                'developerURL': basestring, 
                'developerSupportURL': basestring, 
                'publisher': basestring, 
                'releaseDate': basestring, 
                'price': basestring, 
                'category': basestring, 
                'language': basestring, 
                'rating': basestring, 
                'popularity': basestring, 
                'parentalRating': basestring, 
                'platform': basestring, 
                'requirements': basestring, 
                'size': basestring, 
                'version': basestring, 
                'downloadURL': basestring, 
                'thumbnailURL': basestring, 
                'screenshotURL': basestring, 
                'videoURL': basestring, 
            }, 
            'book': {
                # TODO
            }, 
            'movie': {
                # TODO
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
            }
        }
    }
    
    def __init__(self, setup=False):
        AEntityDB.__init__(self, self.DESC)
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def addEntity(self, entity):
        return self._addDocument(entity)
    
    def getEntity(self, entityId):
        entity = Entity(self._getDocumentFromId(entityId))
        if entity.isValid == False:
            raise KeyError("Entity not valid")
        return entity
        
    def updateEntity(self, entity):
#         return self.getEntity(self._updateDocument(entity))
        self._updateDocument(entity)
        
    def removeEntity(self, entity):
        return self._removeDocument(entity)
    
    def addEntities(self, entities):
        return self._addDocuments(entities)
        
    def matchEntities(self, query, limit=20):
        # Using a simple regex here. Need to rank results at some point...
        query = '^%s' % query
        result = []
        for entity in self._collection.find({"title": {"$regex": query, "$options": "i"}}).limit(limit):
            result.append(Entity(self._mongoToObj(entity)))
        return result
            
    
    ### PRIVATE
        