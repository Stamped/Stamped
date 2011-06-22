#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from AObject import APIObject

class User(APIObject):
    
    def __init__(self, data=None):
        self._data = data or { }
        
        self.id = None
        self.email = None
        self.username = None
        self.name = None
        self.password = None
        self.bio = None
        self.website = None
        self.image = None
        self.privacy = None
        self.account = None
        self.flagged = None
        self.locale = None
        self.timezone = None
        self.other = {}
        