#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from AObject import AObject

class Comment(AObject):

    _schema = {
        'id': basestring,
        'stamp_id': basestring,
        'user': {
            'user_id': basestring,
            'user_name': basestring,
            'user_img': basestring,
            'user_primary_color': basestring,
            'user_secondary_color': basestring
        },
        'restamp_id': basestring,
        'blurb': basestring,
        'mentions': [],
        'timestamp': basestring
    }
    
    def __init__(self, data=None):
        self._data = data or { }
        
    @property
    def isValid(self):
        valid = True
        
        if 'id' in self:
            valid &= isinstance(self.id, basestring) 
        
        valid &= 'stamp_id' in self and isinstance(self.stamp_id, basestring)
        
        valid &= 'user' in self and isinstance(self.user, dict)
        valid &= 'user_id' in self.user and isinstance(self.user['user_id'], basestring)
        valid &= 'user_name' in self.user and isinstance(self.user['user_name'], basestring)
        valid &= 'user_img' in self.user and isinstance(self.user['user_img'], basestring)
        
        
        if 'restamp' in self:
            valid &= isinstance(self.restamp, basestring) 
            valid &= 'user_primary_color' in self.user and isinstance(self.user['user_primary_color'], basestring)
            if 'user_secondary_color' in self.user:
                valid &= isinstance(self.user['user_secondary_color'], basestring)

        valid &= 'blurb' in self and isinstance(self.blurb, basestring)
        valid &= 'timestamp' in self and isinstance(self.timestamp, basestring)
        
        if 'mentions' in self:
            valid &= isinstance(self.mentions, list)
            
        return valid
        