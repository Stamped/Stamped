#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs   import report

try:
    import logs, time

    from api.Schemas import *

    from api.db.mongodb.AMongoCollection import AMongoCollection

    from api.AMenuDB import AMenuDB
except:
    report()
    raise

class MongoMenuCollection(AMongoCollection, AMenuDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='menus', primary_key='entity_id', obj=Menu)
        AMenuDB.__init__(self)

    ### PUBLIC
    def getMenu(self, entityId):
        result = None
        documentId = self._getObjectIdFromString(entityId)
        document = self._collection.find_one(documentId)
        if document is not None:
            result = self._convertFromMongo(document)
        return result
    
    def updateMenu(self, menu):
        self.update(menu)

