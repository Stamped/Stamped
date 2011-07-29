#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from datetime import datetime
from ASchemaBasedAttributeDict import ASchemaBasedAttributeDict

class Activity(ASchemaBasedAttributeDict):
    
    _schema = {
        'activity_id': basestring,
        'genre': basestring, # comment, restamp, favorite, directed, credit milestone
        'user': {
            'user_id': basestring,
            'screen_name': basestring,
            'display_name': basestring,
            'profile_image': basestring,
            'color_primary': basestring,
            'color_secondary': basestring,
            'privacy': bool
        },
        'comment': {
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
        },
        'stamp': {
            'stamp_id': basestring,
            'entity': {
                'entity_id': basestring,
                'title': basestring,
                'coordinates': {
                    'lat': float, 
                    'lng': float
                },
                'category': basestring,
                'subtitle': basestring
            },
            'user': {
                'user_id': basestring,
                'screen_name': basestring,
                'display_name': basestring,
                'profile_image': basestring,
                'color_primary': basestring,
                'color_secondary': basestring,
                'privacy': bool
            },
            'blurb': basestring,
            'image': basestring,
            'mentions': list,
            'credit': list,
            'comment_preview': list,
            'timestamp': {
                'created': datetime,
                'modified': datetime
            },
            'flags': {
                'flagged': bool,
                'locked': bool
            },
            'stats': {
                'num_comments': int,
                'num_todos': int,
                'num_credit': int
            }
        },
        'blurb': basestring,
        'timestamp': {
            'created': datetime
        }
    }
    
    @property
    def isValid(self):
        valid = True
        
        if 'activity_id' in self:
            valid &= isinstance(self.activity_id, basestring) 
            
        valid &= 'genre' in self and isinstance(self.genre, basestring)
        
        # User
        if 'user' in self:
            valid &= isinstance(self.user, dict)
            valid &= 'user_id' in self.user and isinstance(self.user['user_id'], basestring)
            valid &= 'screen_name' in self.user and isinstance(self.user['screen_name'], basestring)
            valid &= 'display_name' in self.user and isinstance(self.user['display_name'], basestring)
            valid &= 'profile_image' in self.user and isinstance(self.user['profile_image'], basestring)
            valid &= 'color_primary' in self.user and isinstance(self.user['color_primary'], basestring)
            if 'color_secondary' in self.user:
                valid &= isinstance(self.user['color_secondary'], basestring)
            valid &= 'privacy' in self.user and isinstance(self.user['privacy'], bool)
        
        # Comment
        if 'comment' in self:
            valid &= isinstance(self.comment, dict)
            valid &= 'comment_id' in self.comment and isinstance(self.comment['comment_id'], basestring)
            valid &= 'stamp_id' in self.comment and isinstance(self.comment['stamp_id'], basestring)
            
            valid &= 'user' in self.comment and isinstance(self.comment['user'], dict)
            valid &= 'user_id' in self.comment['user'] and isinstance(self.comment['user']['user_id'], basestring)
            valid &= 'screen_name' in self.comment['user'] and isinstance(self.comment['user']['screen_name'], basestring)
            valid &= 'display_name' in self.comment['user'] and isinstance(self.comment['user']['display_name'], basestring)
            valid &= 'profile_image' in self.comment['user'] and isinstance(self.comment['user']['profile_image'], basestring)
            valid &= 'color_primary' in self.comment['user'] and isinstance(self.comment['user']['color_primary'], basestring)
            if 'color_secondary' in self.comment['user']:
                valid &= isinstance(self.comment['user']['color_secondary'], basestring)
            valid &= 'privacy' in self.comment['user'] and isinstance(self.comment['user']['privacy'], bool)
            
            valid &= 'blurb' in self.comment and isinstance(self.comment['blurb'], basestring)
            
            valid &= 'timestamp' in self.comment and isinstance(self.comment['timestamp'], dict)
            valid &= 'created' in self.comment['timestamp'] and isinstance(self.comment['timestamp']['created'], datetime)
            
            if 'restamp_id' in self.comment:
                valid &= isinstance(self.comment['restamp_id'], basestring) 
            if 'mentions' in self.comment:
                valid &= isinstance(self.comment['mentions'], list)
        
        # Stamp
        if 'stamp' in self:
            valid &= isinstance(self.stamp, dict) 
#             valid &= 'stamp_id' in self.stamp and isinstance(self.stamp['stamp_id'], basestring)
            ### TODO: Finish this list
        
        valid &= 'timestamp' in self and isinstance(self.timestamp, dict)
        if 'created' in self.timestamp:
            valid &= isinstance(self.timestamp['created'], datetime)  
        
        if 'blurb' in self:
            valid &= isinstance(self.blurb, basestring)
            
        return valid
        
