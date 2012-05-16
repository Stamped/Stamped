#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import datetime, copy
import Globals, utils, logs

from errors import *
from Schemas import *

from AMongoCollection import AMongoCollection
from AAuthEmailAlertsDB import AAuthEmailAlertsDB

class MongoAuthEmailAlertsCollection(AMongoCollection, AAuthEmailAlertsDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='settingsemailalerttokens')
        AAuthEmailAlertsDB.__init__(self)

        self._collection.ensure_index('token_id', unique=True)

    def _convertToMongo(self, token):
        document = token.dataExport()
        if 'user_id' in document:
            document['_id'] = document['user_id']
            del(document['user_id'])
        return document

    def _convertFromMongo(self, document):
        if document != None and '_id' in document:
            document['user_id'] = document['_id']
            del(document['_id'])
        return SettingsEmailAlertToken().dataImport(document)

    ### PUBLIC

    def addToken(self, token):
        logs.debug("Token: %s" % token.token_id)

        document = self._convertToMongo(token)
        document = self._addMongoDocument(document)
        token = self._convertFromMongo(document)

        return token

    def getTokenForUser(self, userId):
        document = self._getMongoDocumentFromId(userId)
        return self._convertFromMongo(document)

    def getTokensForUsers(self, userIds, limit=0):
        query = []
        if isinstance(userIds, list):
            for userId in userIds:
                query.append(userId)

        data = self._collection.find({"_id": {"$in": query}}).limit(limit)
            
        result = []
        for item in data:
            result.append(self._convertFromMongo(item))
        return result
    
    def getToken(self, tokenId):
        document = self._collection.find_one({'token_id': tokenId})
        return self._convertFromMongo(document)
        
    def removeTokenForUser(self, userId):
        return self._removeMongoDocument(userId)
        
    def removeToken(self, tokenId):
        return self._collection.find({'token_id': tokenId})

