#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from ASchemaObject import ASchemaObject
from datetime import datetime

class Account(ASchemaObject):

    _schema = {
        'user_id': basestring,
        'first_name': basestring,
        'last_name': basestring,
        'email': basestring,
        'password': basestring,
        'screen_name': basestring,
        'display_name': basestring,
        'profile_image': basestring,
        'color_primary': basestring,
        'color_secondary': basestring,
        'bio': basestring,
        'website': basestring,
        'privacy': bool,
        'locale': {
            'language': basestring,
            'time_zone': basestring
        },
        'linked_accounts': {
            'itunes': basestring
        },
        'devices': {
            'ios_device_tokens': list
        },
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
        
        if 'user_id' in self:
            valid &= isinstance(self.user_id, basestring) 
        
        valid &= 'first_name' in self and isinstance(self.first_name, basestring)
        valid &= 'last_name' in self and isinstance(self.last_name, basestring)
        valid &= 'email' in self and isinstance(self.email, basestring)
        valid &= 'password' in self and isinstance(self.password, basestring)
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
        
        valid &= 'locale' in self and isinstance(self.locale, dict)
        valid &= 'language' in self.locale and isinstance(self.locale['language'], basestring)
        valid &= 'time_zone' in self.locale and isinstance(self.locale['time_zone'], basestring)
        
        if 'linked_accounts' in self:
            valid &= isinstance(self.linked_accounts, dict) 
            if 'itunes' in self.linked_accounts:
                valid &= isinstance(self.linked_accounts['itunes'], float)
            
        if 'devices' in self:
            valid &= isinstance(self.devices, dict) 
            if 'ios_device_tokens' in self.devices:
                valid &= isinstance(self.devices['ios_device_tokens'], list)
        
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
                
        #valid &= 'timestamp' in self and isinstance(self.timestamp, basestring)
        
        return valid
