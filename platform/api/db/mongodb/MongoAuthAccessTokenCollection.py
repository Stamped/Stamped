#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import datetime, copy
import Globals, utils, logs
import pymongo

from errors import *
from api.Schemas import *

from api.db.mongodb.AMongoCollection import AMongoCollection
from api.AAuthAccessTokenDB import AAuthAccessTokenDB
from libs.Memcache                              import globalMemcache

class MongoAuthAccessTokenCollection(AMongoCollection, AAuthAccessTokenDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='accesstokens')
        AAuthAccessTokenDB.__init__(self)

        self._cache = globalMemcache()

        self._collection.ensure_index([('user_id', pymongo.ASCENDING)])
    
    def _convertToMongo(self, token):
        document = token.dataExport()
        if 'token_id' in document:
            document['_id'] = document['token_id']
            del(document['token_id'])
        return document

    def _convertFromMongo(self, document):
        if document is not None:
            if '_id' in document:
                document['token_id'] = document['_id']
                del(document['_id'])
        return AccessToken().dataImport(document)


    ### CACHING

    def _getCachedToken(self, tokenId):
        key = str("obj::accesstoken::%s" % tokenId)
        return self._cache[key]

    def _setCachedToken(self, token):
        key = str("obj::accesstoken::%s" % token.token_id)
        cacheLength = 60 * 60 # One hour
        try:
            self._cache.set(key, token, time=cacheLength)
        except Exception as e:
            logs.warning("Unable to set cache for %s: %s" % (token.token_id, e))

    def _delCachedToken(self, tokenId):
        key = str("obj::accesstoken::%s" % tokenId)
        try:
            del(self._cache[key])
        except KeyError:
            pass


    ### PUBLIC

    def addAccessToken(self, token):
        logs.debug("Token: %s" % token.token_id)

        document = self._convertToMongo(token)
        document = self._addMongoDocument(document)
        token = self._convertFromMongo(document)
        self._setCachedToken(token)

        return token

    def getAccessToken(self, tokenId):
        try:
            return self._getCachedToken(tokenId)
        except KeyError:
            pass

        document = self._getMongoDocumentFromId(tokenId, forcePrimary=True)
        return self._convertFromMongo(document)
    
    def removeAccessToken(self, tokenId):
        result = self._removeMongoDocument(tokenId)
        self._delCachedToken(tokenId)
        return result

    def removeAccessTokensForUser(self, userId):
        tokens = self._collection.find({'user_id': userId}, fields=['_id'])
        for token in tokens:
            self._delCachedToken(str(token['_id']))

        result = self._collection.remove({'user_id': userId})
        return result