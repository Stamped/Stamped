#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from ASchemaObject import ASchemaObject

class Entity(ASchemaObject):

    _schema = {
        'entity_id': basestring, 
        'title': basestring, 
        'subtitle': basestring,
        'desc': basestring, 
        'locale': basestring, 
        'category': basestring,
        'image': basestring, 
        'timestamp': {
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
    
    def __init__(self, data=None):
        self._data = data or { }
        
    @property
    def isValid(self):
        valid = True
        
        if 'entity_id' in self:
            valid &= isinstance(self.entity_id, basestring) 
        
        valid &= 'title' in self and isinstance(self.title, basestring)
        valid &= 'subtitle' in self and isinstance(self.subtitle, basestring)
        valid &= 'category' in self and isinstance(self.category, basestring)
        
                
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

