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
        'profile_image': basestring,
        'color_primary': basestring,
        'color_secondary': basestring,
        'bio': basestring,
        'website': basestring,
        'privacy': bool,
        'flags': {
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
        
        if 'profile_image' in self and self.profile_image is not None:
            valid &= isinstance(self.profile_image, basestring)
        
        valid &= 'color_primary' in self and isinstance(self.color_primary, basestring)
        if 'color_secondary' in self and self.color_secondary is not None:
            valid &= isinstance(self.color_secondary, basestring)
        
        if 'bio' in self and self.bio is not None:
            valid &= isinstance(self.bio, basestring)
        if 'website' in self and self.website is not None:
            valid &= isinstance(self.website, basestring)
        
        valid &= 'privacy' in self and isinstance(self.privacy, bool)
        
        if 'flags' in self:
            valid &= isinstance(self.flags, dict)
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

