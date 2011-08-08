#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from ASchemaBasedAttributeDict import ASchemaBasedAttributeDict
from datetime import datetime

class AuthRefreshToken(ASchemaBasedAttributeDict):

    _schema = {
        'token_id': basestring,
        'client_id': basestring,
        'authenticated_user_id': basestring,
        'timestamp': {
            'created': datetime,
        },
        'access_tokens': list,
    }
    
    @property
    def isValid(self):
        valid = True
        
        valid &= 'token_id' in self and isinstance(self.token_id, basestring)
        valid &= 'client_id' in self and isinstance(self.client_id, basestring)
        valid &= 'authenticated_user_id' in self and isinstance(self.authenticated_user_id, basestring)
        
        valid &= 'timestamp' in self and isinstance(self.timestamp, dict)
        valid &= 'created' in self.timestamp and isinstance(self.timestamp['created'], datetime)
        
        if 'access_tokens' in self:
            valid &= isinstance(self.access_tokens, list)
        
        return valid

