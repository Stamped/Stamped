#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from datetime import datetime

from AObject import AObject

class Favorite(AObject):

    _schema = {
        'id': basestring,
        'entity': {
            'entity_id': basestring,
            'title': basestring,
            'coordinates': {
                'lat': float, 
                'lng': float
            },
            'category': basestring,
            'subtitle': basestring
        },
        'user': {
            'user_id': basestring,
            'user_name': basestring
        },
        'stamp': {
            'stamp_id': basestring,
            'stamp_blurb': basestring,      # ??
            'stamp_timestamp': basestring,
            'stamp_user_id': basestring,    # ??
            'stamp_user_name': basestring,
            'stamp_user_img': basestring    # ??
        },
        'timestamp': datetime,
        'complete': bool
    }
    
    def __init__(self, data=None):
        self._data = data or { }
        
    @property
    def isValid(self):
        valid = True
        
        if 'id' in self:
            valid &= isinstance(self.id, basestring) 
        
        valid &= 'entity' in self and isinstance(self.entity, dict)
        valid &= 'entity_id' in self.entity and isinstance(self.entity['entity_id'], basestring)
        valid &= 'title' in self.entity and isinstance(self.entity['title'], basestring)
        valid &= 'category' in self.entity and isinstance(self.entity['category'], basestring)
        valid &= 'subtitle' in self.entity and isinstance(self.entity['subtitle'], basestring)
        if 'coordinates' in self.entity:
            valid &= isinstance(self.entity['coordinates'], dict) 
            if 'lat' in self.entity['coordinates']:
                valid &= isinstance(self.entity['coordinates']['lat'], float)
            if 'lng' in self.entity['coordinates']:
                valid &= isinstance(self.entity['coordinates']['lng'], float)
        
        valid &= 'user' in self and isinstance(self.user, dict)
        valid &= 'user_id' in self.user and isinstance(self.user['user_id'], basestring)
        valid &= 'user_name' in self.user and isinstance(self.user['user_name'], basestring)
        
        if 'stamp' in self:
            valid &= isinstance(self.stamp, dict) 
            valid &= 'stamp_id' in self.stamp and isinstance(self.stamp['stamp_id'], basestring)
            valid &= 'stamp_blurb' in self.stamp and isinstance(self.stamp['stamp_blurb'], basestring)
            valid &= 'stamp_timestamp' in self.stamp and isinstance(self.stamp['stamp_timestamp'], basestring)
            valid &= 'stamp_user_id' in self.stamp and isinstance(self.stamp['stamp_user_id'], basestring)
            valid &= 'stamp_user_name' in self.stamp and isinstance(self.stamp['stamp_user_name'], basestring)
            valid &= 'stamp_user_img' in self.stamp and isinstance(self.stamp['stamp_user_img'], basestring)
        
        valid &= 'timestamp' in self and isinstance(self.timestamp, datetime)
        if 'complete' in self:
            valid &= isinstance(self.complete, bool)
            
        return valid
        