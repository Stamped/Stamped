#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals
from MongoEntityCollection import MongoEntityCollection
from AMongoCollection import AMongoCollection

class MongoSearchCacheCollection(AMongoCollection):
    
    def __init__(self, collection='searchcache'):
        AMongoCollection.__init__(self, collection=collection)

