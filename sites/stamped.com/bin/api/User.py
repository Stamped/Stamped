#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from ASchemaBasedAttributeDict import ASchemaBasedAttributeDict
from datetime import datetime

class User(ASchemaBasedAttributeDict):
    
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
            'num_stamps': int,
            'num_following': int,
            'num_followers': int,
            'num_todos': int,
            'num_credit_received': int,
            'num_credit_given': int
        },
        'timestamp': {
            'created': datetime,
            'modified': datetime
        }
    }
    
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
            if 'num_stamps' in self.stats:
                valid &= isinstance(self.stats['num_stamps'], int)
            if 'num_following' in self.stats:
                valid &= isinstance(self.stats['num_following'], int)
            if 'num_followers' in self.stats:
                valid &= isinstance(self.stats['num_followers'], int)
            if 'num_todos' in self.stats:
                valid &= isinstance(self.stats['num_todos'], int)
            if 'num_credit_received' in self.stats:
                valid &= isinstance(self.stats['num_credit_received'], int)
            if 'num_credit_given' in self.stats:
                valid &= isinstance(self.stats['num_credit_given'], int)
        
        return valid

    def _formatHTTP(self, **kwargs):

        output = {}
        output['user_id'] = self.user_id
        output['first_name'] = self.first_name
        output['last_name'] = self.last_name
        output['screen_name'] = self.screen_name
        output['display_name'] = self.display_name
        output['profile_image'] = self.profile_image
        
        if 'bio' in self:
            output['bio'] = self.bio
        else:
            output['bio'] = None
        if 'website' in self:
            output['website'] = self['website']
        else:
            output['website'] = None
        
        output['color_primary'] = self.color_primary
        if 'color_secondary' in self:
            output['color_secondary'] = self.color_secondary
        else:
            output['color_secondary'] = None
        
        output['privacy'] = self.privacy
            
        # if 'stamp' in kwargs:
        ### TODO: Allow us to pass other things here!
        output['last_stamp'] = None
        
        return output
