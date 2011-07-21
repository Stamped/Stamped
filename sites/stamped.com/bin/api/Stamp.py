#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from ASchemaObject import ASchemaObject
from datetime import datetime

class Stamp(ASchemaObject):

    _schema = {
        'stamp_id': basestring,
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
            'screen_name': basestring,
            'display_name': basestring,
            'profile_image': basestring,
            'color_primary': basestring,
            'color_secondary': basestring,
            'privacy': bool
        },
        'blurb': basestring,
        'image': basestring,
        'mentions': list,
        'credit': list,
        'timestamp': {
            'created': datetime,
            'modified': datetime
        },
        'flags': {
            'flagged': bool,
            'locked': bool
        },
        'stats': {
            'num_comments': int,
            'num_todos': int,
            'num_credit': int
        }
    }
    
    def __init__(self, data=None):
        self._data = data or { }
        
    @property
    def isValid(self):
        valid = True
        
        if 'stamp_id' in self:
            valid &= isinstance(self.stamp_id, basestring) 
        
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
        valid &= 'screen_name' in self.user and isinstance(self.user['screen_name'], basestring)
        valid &= 'display_name' in self.user and isinstance(self.user['display_name'], basestring)
        valid &= 'profile_image' in self.user and isinstance(self.user['profile_image'], basestring)
        valid &= 'color_primary' in self.user and isinstance(self.user['color_primary'], basestring)
        if 'color_secondary' in self.user:
            valid &= isinstance(self.user['color_secondary'], basestring)
        valid &= 'privacy' in self.user and isinstance(self.user['privacy'], bool)
        
        valid &= 'timestamp' in self and isinstance(self.timestamp, dict)
        valid &= 'created' in self.timestamp and isinstance(self.timestamp['created'], datetime)
        
        if 'blurb' in self:
            valid &= isinstance(self.blurb, basestring)
        if 'image' in self:
            valid &= isinstance(self.image, basestring)
        if 'mentions' in self:
            valid &= isinstance(self.mentions, list)
        if 'credit' in self:
            valid &= isinstance(self.credit, list)
        
        if 'flags' in self:
            valid &= isinstance(self.flags, dict)
            if 'flagged' in self.flags:
                valid &= isinstance(self.flags['flagged'], bool)
            if 'locked' in self.flags:
                valid &= isinstance(self.flags['locked'], bool)
        
        if 'stats' in self:
            valid &= isinstance(self.stats, dict) 
            if 'num_comments' in self.stats:
                valid &= isinstance(self.stats['num_comments'], int)
            if 'num_todos' in self.stats:
                valid &= isinstance(self.stats['num_todos'], int)
            if 'num_credit' in self.stats:
                valid &= isinstance(self.stats['num_credit'], int)
        
        return valid
        
