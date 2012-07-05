#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs       import report

try:
    from datetime                       import datetime
    from utils                          import lazyProperty

    from api.Schemas                        import *
    from api.Entity                         import getSimplifiedTitle, buildEntity

    from api.db.mongodb.AMongoCollection               import AMongoCollection
    from api.AEntityDB                      import AEntityDB
    from errors                         import StampedUnavailableError
    from logs                           import log
except:
    report()
    raise


class MongoEntitySeedCollection(AMongoCollection, AEntityDB):
    
    def __init__(self, collection='entities'):
        AMongoCollection.__init__(self, collection='seedentities', primary_key='entity_id', overflow=True)
        AEntityDB.__init__(self)
    
    def _convertFromMongo(self, document):
        if document is None:
            return None

        if '_id' in document and self._primary_key is not None:
            document[self._primary_key] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])

        document.pop('titlel')

        entity = buildEntity(document)
        
        return entity
    
    def _convertToMongo(self, entity):
        if entity.entity_id is not None and entity.entity_id.startswith('T_'):
            del entity.entity_id
        document = AMongoCollection._convertToMongo(self, entity)
        if document is None:
            return None
        if 'title' in document:
            document['titlel'] = getSimplifiedTitle(document['title'])
        return document
    
    ### PUBLIC
    
    def addEntity(self, entity):
        return self._addObject(entity)

