#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from AObject import APIObject

class Stamp(APIObject):
    
    def __init__(self, data=None):
        self._data = data or { }
        
        self.id = None
        self.entity_id = None
        self.user_id = None
        self.comment = None
        self.image = None
        self.flagged = None
        self.date_created = None
        self.other = {}
