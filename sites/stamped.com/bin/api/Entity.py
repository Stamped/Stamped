#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
from ASchemaBasedAttributeDict import ASchemaBasedAttributeDict

categories = set([ 'food', 'music', 'film', 'book', 'other' ])
subcategories = {
    'restaurant' : 'food', 
    'book' : 'book', 
    'movie' : 'film', 
    'artist' : 'music', 
    'song' : 'music', 
    'album' : 'music', 
    'app' : 'other', 
    'other' : 'other',
}

class Entity(ASchemaBasedAttributeDict):
    
    _schema = {
        'entity_id': basestring, 
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
            'zagat' : {
                'zurl' : basestring, 
            }, 
            'urbanspoon' : {
                'uurl' : basestring, 
            }, 
            'nymag' : { }, 
        }
    }
    
    @property
    def isValid(self):
        valid = True
        
        if 'entity_id' in self:
            valid &= isinstance(self.entity_id, basestring) 
            #utils.logs.debug('isValid: %s (entity.entity_id)' % valid)
        
        valid &= 'title' in self and isinstance(self.title, basestring)
        self.title = self.title.strip()
        #utils.logs.debug('isValid: %s (entity.title)' % valid)
        
        valid &= 'subcategory' in self and isinstance(self.subcategory, basestring)
        #utils.logs.debug('isValid: %s (entity.category)' % valid)
        valid &= self.subcategory in subcategories
        #utils.logs.debug('isValid: %s (entity.subcategory)' % valid)
        
        if not 'category' in self:
            self.category = subcategories[self.subcategory]
        
        valid &= 'category' in self and isinstance(self.category, basestring)
        #utils.logs.debug('isValid: %s (entity.category)' % valid)
        valid &= self.category in categories 
        #utils.logs.debug('isValid: %s (entity.category)' % valid)
        valid &= self.category == subcategories[self.subcategory]
        #utils.logs.debug('isValid: %s (entity.category)' % valid)
        
        if not 'subtitle' in self:
            self.subtitle = self.category
        valid &= 'subtitle' in self and isinstance(self.subtitle, basestring)
        #utils.logs.debug('isValid: %s (entity.subtitle)' % valid)
        
#         if 'website' in self:
#             valid &= isinstance(self.website, basestring)
#         if 'bio' in self:
#             valid &= isinstance(self.bio, basestring)
#             
#         valid &= 'colors' in self and isinstance(self.colors, dict)
#         valid &= 'primary_color' in self.colors and isinstance(self.colors['primary_color'], basestring)
#         if 'secondary_color' in self.colors:
#             valid &= isinstance(self.colors['secondary_color'], basestring)
#             
#         if 'linked_accounts' in self:
#             valid &= isinstance(self.linked_accounts, dict) 
#             if 'itunes' in self.linked_accounts:
#                 valid &= isinstance(self.linked_accounts['itunes'], float)
#         
#         valid &= 'flags' in self and isinstance(self.flags, dict)
#         valid &= 'privacy' in self.flags and isinstance(self.flags['privacy'], bool)
#         if 'flagged' in self.flags:
#             valid &= isinstance(self.flags['flagged'], bool)
#         if 'locked' in self.flags:
#             valid &= isinstance(self.flags['locked'], bool)
#             
#         if 'stats' in self:
#             valid &= isinstance(self.stats, dict) 
#             if 'total_stamps' in self.stats:
#                 valid &= isinstance(self.stats['total_stamps'], int)
#             if 'total_following' in self.stats:
#                 valid &= isinstance(self.stats['total_following'], int)
#             if 'total_followers' in self.stats:
#                 valid &= isinstance(self.stats['total_followers'], int)
#             if 'total_todos' in self.stats:
#                 valid &= isinstance(self.stats['total_todos'], int)
#             if 'total_credit_received' in self.stats:
#                 valid &= isinstance(self.stats['total_credit_received'], int)
#             if 'total_credit_given' in self.stats:
#                 valid &= isinstance(self.stats['total_credit_given'], int)
        
        return valid

