#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from ASchemaBasedAttributeDict import ASchemaBasedAttributeDict

class Friendship(ASchemaBasedAttributeDict):
    
    _schema = {
        'user_id': basestring,
        'friend_id': basestring,
        'timestamp': basestring
    }
    
    @property
    def isValid(self):
        valid = True
        
        valid &= 'user_id' in self and isinstance(self.user_id, basestring)
        valid &= 'friend_id' in self and isinstance(self.friend_id, basestring)
        
        if 'timestamp' in self:
            valid &= isinstance(self.timestamp, basestring)
        
        return valid

