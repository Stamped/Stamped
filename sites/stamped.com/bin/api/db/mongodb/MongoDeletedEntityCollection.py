#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__   = "TODO"

import Globals
from MongoEntityCollection import MongoEntityCollection

class MongoDeletedEntityCollection(MongoEntityCollection):
    
    def __init__(self):
        MongoEntityCollection.__init__(self, collection='deletedentities')

