#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from AObject import AObject

class Stamp(AObject):

    _schema = {
        '_id': object,
        'entity': {
            'entity_id': object,
            'title': basestring,
            'coordinates': {
                'lat': float, 
                'lng': float
            },
            'category': basestring,
            'subtitle': basestring
        },
        'user': {
            'user_id': object,
            'user_name': basestring,
            'user_img': basestring,
        },
        'blurb': basestring,
        'img': basestring,
        'mentions': list,
        'credit': list,
        'timestamp': basestring,
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
        
        if '_id' in self:
            valid &= isinstance(self._id, object) 
        
        valid &= 'entity' in self and isinstance(self.entity, dict)
#         valid &= 'entity_id' in self and isinstance(self.entity_id, object)
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
#         valid &= 'user_id' in self and isinstance(self.user_id, object)
        valid &= 'user_name' in self.user and isinstance(self.user['user_name'], basestring)
        valid &= 'user_img' in self.user and isinstance(self.user['user_img'], basestring)
        
        valid &= 'timestamp' in self and isinstance(self.timestamp, basestring)
        if 'blurb' in self:
            valid &= isinstance(self.blurb, basestring)
        if 'img' in self:
            valid &= isinstance(self.img, basestring)
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
        
