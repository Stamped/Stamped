#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from AObject import AObject
from datetime import datetime

class Stamp(AObject):

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
            'user_display_name': basestring,
            'user_image': basestring,
            'user_color': {
                'primary': list,
                'secondary': list
            }
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
            'privacy': bool,
            'flagged': bool,
            'locked': bool
        },
        'stats': {
            'total_comments': int,
            'total_todos': int,
            'total_credit': int
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
        valid &= 'user_display_name' in self.user and isinstance(self.user['user_display_name'], basestring)
        valid &= 'user_image' in self.user and isinstance(self.user['user_image'], basestring)
        valid &= 'user_color' in self.user and isinstance(self.user['user_color'], dict)
        valid &= 'primary' in self.user['user_color'] and isinstance(self.user['user_color']['primary'], list)
        
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
        
        valid &= 'flags' in self and isinstance(self.flags, dict)
        valid &= 'privacy' in self.flags and isinstance(self.flags['privacy'], bool)
        if 'flagged' in self.flags:
            valid &= isinstance(self.flags['flagged'], bool)
        if 'locked' in self.flags:
            valid &= isinstance(self.flags['locked'], bool)
        
        if 'stats' in self:
            valid &= isinstance(self.stats, dict) 
            if 'total_comments' in self.stats:
                valid &= isinstance(self.stats['total_comments'], int)
            if 'total_todos' in self.stats:
                valid &= isinstance(self.stats['total_todos'], int)
            if 'total_credit' in self.stats:
                valid &= isinstance(self.stats['total_credit'], int)
        
        return valid
        
