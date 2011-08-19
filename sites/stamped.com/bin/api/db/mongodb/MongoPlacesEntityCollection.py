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
from datetime import datetime

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
            'created' : datetime, 
            'modified': datetime, 
        }, 
        'coordinates': list, 
        'details': {
            'place': {
                'address': basestring, 
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
                'mpaa_rating' : basestring, 
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
            'sfmag' : { }, 
            'latimes' : { },
            'bostonmag' : { }, 
            'fandango' : {
                "fid" : basestring, 
            }, 
            'chicagomag' : { },
            'phillymag' : { }, 
            'netflix' : {
                'nid' : int, 
                'nrating' : float, 
                'ngenres' : list, 
                'nurl' : basestring, 
                'images' : {
                    'tiny'  : basestring, 
                    'small' : basestring, 
                    'large' : basestring, 
                    'hd'    : basestring, 
                }, 
            }, 

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
        return entity
    
    def updateEntity(self, entity):
        return self._updateDocument(entity, 'entity_id')
    
    def removeEntity(self, entityID):
        return self._removeDocument(entityID)
    
    def addEntities(self, entities):
        return self._addDocuments(entities, 'entity_id')
    
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

