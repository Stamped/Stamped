#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals

from AMongoCollection import AMongoCollection
from api.AEntityDB import AEntityDB
from api.Entity import Entity

class MongoEntityCollection(AMongoCollection, AEntityDB):
    
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
            'iPhoneApp': {
                'developer': basestring, 
                'developerURL': basestring, 
                'developerSupportURL': basestring, 
                'publisher': basestring, 
                'releaseDate': basestring, 
                'appCategory': basestring, 
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
            'video': {
                # TODO: modify types
                'studio_name': basestring, 
                'network_name': basestring, 
                'short_description': basestring, 
                'long_description': basestring, 
                'episode_production_number': basestring, 
                #'price' : {
                #    'retail_price' : basestring, 
                #    'currency_code' : basestring, 
                #    'storefront_id' : basestring, 
                #    'availability_date' : basestring, 
                #    'sd_price' : basestring, 
                #    'hq_price' : basestring, 
                #    'lc_rental_price' : basestring, 
                #    'sd_rental_price' : basestring, 
                #    'hd_rental_price' : basestring, 
                #}, 
            }, 
            'artist' : {
                'albums' : list, 
            }, 
            'song': {
                'preview_url': basestring, 
                'preview_length': basestring, 
            }, 
            'album' : {
                'label_studio'   : basestring, 
                'is_compilation' : bool, 
            }, 
            'media' : {
                'title_version': basestring, 
                'search_terms': basestring, 
                'parental_advisory_id': basestring, 
                'artist_display_name': basestring, 
                'collection_display_name': basestring, 
                'original_release_date': basestring, 
                'itunes_release_date': basestring, 
                'track_length': basestring, 
                'copyright': basestring, 
                'p_line': basestring, 
                'content_provider_name': basestring, 
                'media_type_id': basestring, 
                'artwork_url': basestring, 
            }, 
        }, 
        'sources': {
            'apple' : {
                'aid' : basestring, 
                'export_date' : basestring, 
                'is_actual_artist' : bool, 
                'view_url' : basestring, 
                'match' : {
                    'upc' : basestring, 
                    'isrc' : basestring, 
                    'grid' : basestring, 
                    'amg_video_id' : basestring, 
                    'amg_track_id' : basestring, 
                    'isan' : basestring, 
                }, 
            }, 
        }
    }
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='entities')
        AEntityDB.__init__(self)
    
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

