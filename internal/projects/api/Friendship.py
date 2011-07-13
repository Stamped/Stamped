#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from AObject import AObject

class Friendship(AObject):

    _schema = {
        'user_id': basestring,
        'following_id': basestring,
        'timestamp': basestring
    }
    
    def __init__(self, data=None):
        self._data = data or { }
        
    @property
    def isValid(self):
        valid = True
        
        valid &= 'user_id' in self and isinstance(self.user_id, basestring)
        valid &= 'following_id' in self and isinstance(self.following_id, basestring)
        
        if 'timestamp' in self:
            valid &= isinstance(self.timestamp, basestring)
        
        return valid
        