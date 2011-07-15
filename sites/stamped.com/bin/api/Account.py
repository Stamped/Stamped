#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from AObject import AObject

class Account(AObject):

    _schema = {
        'id': basestring,
        'first_name': basestring,
        'last_name': basestring,
        'username': basestring,
        'email': basestring,
        'password': basestring,
        'img': basestring,
        'locale': basestring,
        'timestamp': basestring,
        'website': basestring,
        'bio': basestring,
        'color': {
            'primary_color': basestring,
            'secondary_color': basestring
        },
        'linked_accounts': {
            'itunes': basestring
        },
        'devices': {
            'ios_device_tokens': list
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
        valid &= 'username' in self and isinstance(self.username, basestring)
        valid &= 'email' in self and isinstance(self.email, basestring)
        valid &= 'password' in self and isinstance(self.password, basestring)
        valid &= 'locale' in self and isinstance(self.locale, basestring)
        #valid &= 'timestamp' in self and isinstance(self.timestamp, basestring)
        
        if 'img' in self and self.img is not None:
            valid &= isinstance(self.img, basestring)
        if 'website' in self and self.website is not None:
            valid &= isinstance(self.website, basestring)
        if 'bio' in self and self.bio is not None:
            valid &= isinstance(self.bio, basestring)
        
        
        valid &= 'color' in self and isinstance(self.color, dict)
        valid &= 'primary_color' in self.color and isinstance(self.color['primary_color'], basestring)
        
        # TODO: there's something weird going on here, where self.color.secondary_color is None, but 
        # it's not being equality tested against None... fuck off, Python!
        #if 'secondary_color' in self.color and self.color.secondary_color is not None:
        #print str(self.color['secondary_color'])
        #print repr(self.color['secondary_color'])
        #print str(type(self.color['secondary_color']))
        #    valid &= isinstance(self.color['secondary_color'], basestring)
        
        if 'linked_accounts' in self:
            valid &= isinstance(self.linked_accounts, dict) 
            if 'itunes' in self.linked_accounts:
                valid &= isinstance(self.linked_accounts['itunes'], float)
            
        if 'devices' in self:
            valid &= isinstance(self.devices, dict) 
            if 'ios_device_tokens' in self.devices:
                valid &= isinstance(self.devices['ios_device_tokens'], list)
        
        valid &= 'flags' in self and isinstance(self.flags, dict)
        valid &= 'privacy' in self.flags and isinstance(self.flags['privacy'], bool)
        
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
