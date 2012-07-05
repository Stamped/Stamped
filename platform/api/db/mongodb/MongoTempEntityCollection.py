#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from api.db.mongodb.MongoEntityCollection import MongoEntityCollection

class MongoTempEntityCollection(MongoEntityCollection):
    
    def __init__(self):
        MongoEntityCollection.__init__(self, collection='tempentities')

