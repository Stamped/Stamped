#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from datetime import datetime
from ASchemaObject import ASchemaObject

class Favorite(ASchemaObject):

    _schema = {
        'favorite_id': basestring,
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
        'user_id': basestring,
        'stamp': {
            'stamp_id': basestring,
            'display_name': basestring
        },
        'timestamp': {
            'created': datetime,
            'modified': datetime
        },
        'complete': bool
    }
    
    def __init__(self, data=None):
        self._data = data or { }
        
    @property
    def isValid(self):
        valid = True
        
        if 'favorite_id' in self:
            valid &= isinstance(self.favorite_id, basestring) 
        
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
        
        valid &= 'user_id' in self and isinstance(self.user_id, basestring)
        
        if 'stamp' in self:
            valid &= isinstance(self.stamp, dict) 
            valid &= 'stamp_id' in self.stamp and isinstance(self.stamp['stamp_id'], basestring)
            valid &= 'display_name' in self.stamp and isinstance(self.stamp['display_name'], basestring)
        
        valid &= 'timestamp' in self and isinstance(self.timestamp, dict)
        if 'created' in self.timestamp:
            valid &= isinstance(self.timestamp['created'], datetime) 
        if 'modified' in self.timestamp:
            valid &= isinstance(self.timestamp['modified'], datetime) 
        
        if 'complete' in self:
            valid &= isinstance(self.complete, bool)
            
        return valid
        
