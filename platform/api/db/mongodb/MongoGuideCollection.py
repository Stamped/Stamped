#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, logs, time

from datetime import datetime
from utils import lazyProperty
from api.Schemas import *

from api.db.mongodb.AMongoCollection import AMongoCollection

class MongoGuideCollection(AMongoCollection):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='guides', primary_key='user_id', obj=GuideCache)

    def _convertFromMongo(self, document):
        if document is None:
            return None

        # Temporary transition (dev only - not necessary on prod)
        if 'updated' in document:
            if 'timestamp' not in document:
                document['timestamp'] = {'generated': document['update']}

        return AMongoCollection._convertFromMongo(self, document)

    ### INTEGRITY

    def checkIntegrity(self, key, repair=False, api=None):
        """
        Check a stamp's stats to verify the following things:

        - Stamp still exists 

        - Stats are not out of date 

        """

        regenerate = False
        document = None

        # Remove stat if user no longer exists
        if self._collection._database['users'].find({'_id': key}).count() == 0:
            msg = "%s: User no longer exists"
            if repair:
                logs.info(msg)
                self._removeMongoDocument(key)
                return True
            else:
                raise StampedDataError(msg)
        
        # Verify stat exists
        try:
            document = self._getMongoDocumentFromId(key)
        except StampedDocumentNotFoundError:
            msg = "%s: Stat not found" % key
            if repair:
                logs.info(msg)
                regenerate = True
            else:
                raise StampedDataError(msg)

        # Check if old schema version
        if 'timestamp' not in document:
            msg = "%s: Old schema" % key
            if repair:
                logs.info(msg)
                regenerate = True
            else:
                raise StampedDataError(msg)

        # Check if stats are stale
        elif document is not None and 'timestamp' in document:
            generated = document['timestamp']['generated']
            if generated < datetime.utcnow() - timedelta(days=2):
                msg = "%s: Stale stats" % key
                if repair:
                    logs.info(msg)
                    regenerate = True 
                else:
                    raise StampedDataError(msg)

        # Rebuild
        if regenerate and repair:
            if api is not None:
                api.buildGuideAsync(str(key), force=True)
            else:
                raise Exception("%s: API required to regenerate stats" % key)

        return True
    
    ### PUBLIC
    
    def addGuide(self, guide):
        if guide.timestamp is None:
            guide.timestamp = StatTimestamp()
        guide.timestamp.generated = datetime.utcnow()

        return self._addObject(guide)
    
    def removeGuide(self, userId):
        documentId = self._getObjectIdFromString(userId)
        return self._removeMongoDocument(documentId)
    
    def getGuide(self, userId):
        documentId = self._getObjectIdFromString(userId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)

    def updateGuide(self, guide):
        if guide.timestamp is None:
            guide.timestamp = StatTimestamp()
        guide.timestamp.generated = datetime.utcnow()

        return self.update(guide)

