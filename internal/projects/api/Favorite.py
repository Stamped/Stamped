#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from AObject import AObject

class Favorite(AObject):
    
    def __init__(self, data=None):
        self._data = data or { }
        
        self.stampID = None
        self.userID = None
        self.timestamp = None
        