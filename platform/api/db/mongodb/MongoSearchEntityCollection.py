#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils, datetime, hashlib
from api.Schemas import BasicEntity
from api.db.mongodb.AMongoCollectionView import AMongoCollectionView
from api.ASearchEntityDB import ASearchEntityDB
from api.Entity                         import buildEntity

SEARCH_ENTITY_TTL = datetime.timedelta(1)  # Search entities persist for a day.

class MongoSearchEntityCollection(AMongoCollectionView, ASearchEntityDB):
    def __init__(self):
        AMongoCollectionView.__init__(self, collection='search_entities', obj=BasicEntity, overflow=True)
        ASearchEntityDB.__init__(self)
        self._ttl = datetime.timedelta(1)

    def _searchIdToCollectionKey(self, searchId):
        result = hashlib.sha224(searchId).hexdigest()[:24]
        print 'RETURNING', result
        return result

    # Mongo conversions work a little differently because the key -- search_id -- is not a proper field of the
    # BasicEntity schema, it is just a lazyProperty. Also, we tag on an expiration date.
    # TODO: We should really have a top-level dictionary that contains an _id, an expiration, and a sub-dictionary with
    # the entity contents.
    def _convertFromMongo(self, document):
        if document is None:
            return None

        if '_id' in document:
            del(document['_id'])
        if 'expiration' in document:
            del(document['expiration'])

        return buildEntity(document)

    def _convertToMongo(self, obj):
        if obj is None:
            return None

        if self._obj is not None:
            assert isinstance(obj, self._obj)

        try:
            document = obj.dataExport()
        except (NameError, AttributeError):
            document = obj

        document['_id'] = self._getObjectIdFromString(self._searchIdToCollectionKey(obj.search_id))
        document['expiration'] = datetime.datetime.now() + self._ttl
        return document

    def getSearchEntityBySearchId(self, search_id):
        documentId = self._getObjectIdFromString(self._searchIdToCollectionKey(search_id))
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)

    def writeSearchEntity(self, search_entity):
        self.update(search_entity)