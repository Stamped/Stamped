#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
from MongoEntityCollection import MongoEntityCollection

class MongoTempEntityCollection(MongoEntityCollection):
    
    def __init__(self):
        MongoEntityCollection(collection='tempentities')

