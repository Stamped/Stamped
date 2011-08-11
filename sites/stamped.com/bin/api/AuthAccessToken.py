#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils, logs
from ASchemaBasedAttributeDict import ASchemaBasedAttributeDict
from datetime import datetime

class AuthAccessToken(ASchemaBasedAttributeDict):

    _schema = {
        'token_id': basestring,
        'client_id': basestring,
        'refresh_token': basestring,
        'authenticated_user_id': basestring,
        'expires': datetime,
        'timestamp': {
            'created': datetime,
        },
    }
    
    @property
    def isValid(self):
        valid = True
        
        valid &= 'token_id' in self and isinstance(self.token_id, basestring)
        # logs.debug('isValid: %s (token.token_id)' % valid)

        valid &= 'client_id' in self and isinstance(self.client_id, basestring)
        # logs.debug('isValid: %s (token.client_id)' % valid)

        valid &= 'refresh_token' in self and isinstance(self.refresh_token, basestring)
        # logs.debug('isValid: %s (token.refresh_token)' % valid)

        valid &= 'authenticated_user_id' in self and isinstance(self.authenticated_user_id, basestring)
        # logs.debug('isValid: %s (token.authenticated_user_id)' % valid)

        valid &= 'expires' in self and isinstance(self.expires, datetime)
        # logs.debug('isValid: %s (token.expires)' % valid)
        
        valid &= 'timestamp' in self and isinstance(self.timestamp, dict)
        valid &= 'created' in self.timestamp and isinstance(self.timestamp['created'], datetime)
        # logs.debug('isValid: %s (token.timestamp)' % valid)
        
        return valid
