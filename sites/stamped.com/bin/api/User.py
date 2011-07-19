#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from AObject import AObject
from datetime import datetime

class User(AObject):

    _schema = {
        'user_id': basestring,
        'first_name': basestring,
        'last_name': basestring,
        'screen_name': basestring,
        'display_name': basestring,
        'image': basestring,
        'bio': basestring,
        'website': basestring,
        'color': {
            'primary': list,
            'secondary': list
        },
        'flags': {
            'privacy': bool,
            'flagged': bool,
            'locked': bool
        },
        'stats': {
            'total_stamps': int,
            'total_following': int,
            'total_followers': int,
            'total_todos': int,
            'total_credit_received': int,
            'total_credit_given': int
        },
        'timestamp': {
            'created': datetime,
            'modified': datetime
        }
    }
    
    def __init__(self, data=None):
        self._data = data or { }
        
    @property
    def isValid(self):
        valid = True
        
        if 'id' in self:
            valid &= isinstance(self.id, basestring) 
        
        valid &= 'first_name' in self and isinstance(self.first_name, basestring)
        valid &= 'last_name' in self and isinstance(self.last_name, basestring)
        valid &= 'screen_name' in self and isinstance(self.screen_name, basestring)
        valid &= 'display_name' in self and isinstance(self.display_name, basestring)
        
        valid &= 'color' in self and isinstance(self.color, dict)
        valid &= 'primary' in self.color and isinstance(self.color['primary'], list) and len(self.color['primary']) == 3
        
        valid &= 'flags' in self and isinstance(self.flags, dict)
        valid &= 'privacy' in self.flags and isinstance(self.flags['privacy'], bool)
        
        if 'image' in self and self.image is not None:
            valid &= isinstance(self.image, basestring)
        if 'website' in self and self.website is not None:
            valid &= isinstance(self.website, basestring)
        if 'bio' in self and self.bio is not None:
            valid &= isinstance(self.bio, basestring)
        
        if 'secondary' in self.color and self.color['secondary'] is not None:
            valid &= isinstance(self.color['secondary'], list) and len(self.color['secondary']) == 3
        
        if 'flagged' in self.flags:
            valid &= isinstance(self.flags['flagged'], bool)
        if 'locked' in self.flags:
            valid &= isinstance(self.flags['locked'], bool)
            
        if 'stats' in self:
            valid &= isinstance(self.stats, dict) 
            if 'total_stamps' in self.stats:
                valid &= isinstance(self.stats['total_stamps'], int)
            if 'total_following' in self.stats:
                valid &= isinstance(self.stats['total_following'], int)
            if 'total_followers' in self.stats:
                valid &= isinstance(self.stats['total_followers'], int)
            if 'total_todos' in self.stats:
                valid &= isinstance(self.stats['total_todos'], int)
            if 'total_credit_received' in self.stats:
                valid &= isinstance(self.stats['total_credit_received'], int)
            if 'total_credit_given' in self.stats:
                valid &= isinstance(self.stats['total_credit_given'], int)
        
        return valid

