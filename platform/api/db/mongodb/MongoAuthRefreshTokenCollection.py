#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import datetime, copy
import Globals, utils, logs

from errors import *
from api.Schemas import *

from AMongoCollection import AMongoCollection
from AAuthRefreshTokenDB import AAuthRefreshTokenDB

class MongoAuthRefreshTokenCollection(AMongoCollection, AAuthRefreshTokenDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='refreshtokens')
        AAuthRefreshTokenDB.__init__(self)
    
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
        return RefreshToken().dataImport(document)

    ### PUBLIC

    def addRefreshToken(self, token):
        logs.debug("Token: %s" % token.token_id)

        document = self._convertToMongo(token)
        document = self._addMongoDocument(document)
        token = self._convertFromMongo(document)

        return token

    def getRefreshToken(self, tokenId):
        document = self._getMongoDocumentFromId(tokenId)
        return self._convertFromMongo(document)
    
    def removeRefreshToken(self, tokenId):
        return self._removeMongoDocument(tokenId)

    def removeRefreshTokensForUser(self, userId):
        return self._collection.remove({'user_id': userId})
        
