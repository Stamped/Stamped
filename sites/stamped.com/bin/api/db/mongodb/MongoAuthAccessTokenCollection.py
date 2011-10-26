#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import datetime, copy
import Globals, utils, logs

from errors import *
from Schemas import *

from AMongoCollection import AMongoCollection
from AAuthAccessTokenDB import AAuthAccessTokenDB

class MongoAuthAccessTokenCollection(AMongoCollection, AAuthAccessTokenDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='accesstokens')
        AAuthAccessTokenDB.__init__(self)
    
    def _convertToMongo(self, token):
        document = token.value
        if 'token_id' in document:
            document['_id'] = document['token_id']
            del(document['token_id'])
        return document

    def _convertFromMongo(self, document):
        if document != None and '_id' in document:
            document['token_id'] = document['_id']
            del(document['_id'])
        return AccessToken(document)

    ### PUBLIC

    def addAccessToken(self, token):
        logs.debug("Token: %s" % token.token_id)

        document = self._convertToMongo(token)
        document = self._addMongoDocument(document)
        token = self._convertFromMongo(document)

        return token

    def getAccessToken(self, tokenId):
        document = self._getMongoDocumentFromId(tokenId)
        return self._convertFromMongo(document)
    
    def removeAccessToken(self, tokenId):
        return self._removeMongoDocument(tokenId)

    def removeAccessTokensForUser(self, userId):
        return self._collection.remove({'user_id': userId})

