#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from AObject import AObject

class Friendship(AObject):
    
    def __init__(self, data=None):
        self._data = data or { }
        
        self.userID = None
        self.followingID = None
        self.timestamp = None
        self.approved = None
        