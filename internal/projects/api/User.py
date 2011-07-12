#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from AObject import AObject

class User(AObject):

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
        'colors': {
            'primary_color': basestring,
            'secondary_color': basestring
        },
        'linked_accounts': {
            'itunes': basestring
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
        valid &= 'img' in self and isinstance(self.img, basestring)
        valid &= 'locale' in self and isinstance(self.locale, basestring)
        valid &= 'timestamp' in self and isinstance(self.timestamp, basestring)
        
        if 'website' in self:
            valid &= isinstance(self.website, basestring)
        if 'bio' in self:
            valid &= isinstance(self.bio, basestring)
            
        valid &= 'colors' in self and isinstance(self.colors, dict)
        valid &= 'primary_color' in self.colors and isinstance(self.colors['primary_color'], basestring)
        if 'secondary_color' in self.colors:
            valid &= isinstance(self.colors['secondary_color'], basestring)
            
        if 'linked_accounts' in self:
            valid &= isinstance(self.linked_accounts, dict) 
            if 'itunes' in self.linked_accounts:
                valid &= isinstance(self.linked_accounts['itunes'], float)
        
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
