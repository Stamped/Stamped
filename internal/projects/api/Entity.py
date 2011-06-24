#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from AObject import AObject

class Entity(AObject):
    
    def __init__(self, data=None):
        self._data = data or { }
        
        self.id = None
        self.title = None
        self.description = None
        self.category = None
        self.image = None
        self.source = None
        self.location = None
        self.locale = None
        self.date_created = None
        self.date_updated = None
        self.other = {}
