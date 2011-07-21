#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from ASchemaObject import ASchemaObject
from datetime import datetime

class Comment(ASchemaObject):

    _schema = {
        'comment_id': basestring,
        'stamp_id': basestring,
        'user': {
            'user_id': basestring,
            'screen_name': basestring,
            'display_name': basestring,
            'profile_image': basestring,
            'color_primary': basestring,
            'color_secondary': basestring,
            'privacy': bool
        },
        'restamp_id': basestring,
        'blurb': basestring,
        'mentions': [],
        'timestamp': {
            'created': datetime
        }
    }
    
    def __init__(self, data=None):
        self._data = data or { }
        
    @property
    def isValid(self):
        valid = True
        
        if 'comment_id' in self:
            valid &= isinstance(self.comment_id, basestring) 
        
        valid &= 'stamp_id' in self and isinstance(self.stamp_id, basestring)
        
        valid &= 'user' in self and isinstance(self.user, dict)
        valid &= 'user_id' in self.user and isinstance(self.user['user_id'], basestring)
        valid &= 'screen_name' in self.user and isinstance(self.user['screen_name'], basestring)
        valid &= 'display_name' in self.user and isinstance(self.user['display_name'], basestring)
        valid &= 'profile_image' in self.user and isinstance(self.user['profile_image'], basestring)
        valid &= 'color_primary' in self.user and isinstance(self.user['color_primary'], basestring)
        if 'color_secondary' in self.user:
            valid &= isinstance(self.user['color_secondary'], basestring)
        valid &= 'privacy' in self.user and isinstance(self.user['privacy'], bool)
        
        valid &= 'blurb' in self and isinstance(self.blurb, basestring)
        
        valid &= 'timestamp' in self and isinstance(self.timestamp, dict)
        valid &= 'created' in self.timestamp and isinstance(self.timestamp['created'], datetime)
        
        if 'restamp_id' in self:
            valid &= isinstance(self.restamp_id, basestring) 
        if 'mentions' in self:
            valid &= isinstance(self.mentions, list)
            
        return valid
        
