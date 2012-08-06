#!/usr/bin/env python
from __future__ import absolute_import

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals, pymongo

from api.db.mongodb.AMongoCollection   import AMongoCollection
from api.Schemas            import ClientLogsEntry

class MongoClientLogsCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='clientlogs', 
                                  primary_key='entry_id', obj=ClientLogsEntry)
        
        self._collection.ensure_index('user_id', unique=False)
        self._collection.ensure_index('key',     unique=False)
    
    ### PUBLIC
    
    def addEntry(self, entry):
        return self._addObject(entry)
    
    def addEntries(self, entries):
        return self._addObjects(entries)

