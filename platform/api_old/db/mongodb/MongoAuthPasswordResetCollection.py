#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import datetime, copy
import Globals, utils, logs, pymongo

from errors import *
from api_old.Schemas import *

from db.mongodb.AMongoCollection import AMongoCollection
from api_old.AAuthPasswordResetDB import AAuthPasswordResetDB

class MongoAuthPasswordResetCollection(AMongoCollection, AAuthPasswordResetDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='passwordreset')
        AAuthPasswordResetDB.__init__(self)

        self._collection.ensure_index([('user_id', pymongo.ASCENDING)])
    
    def _convertToMongo(self, token):
        document = token.dataExport()
        if 'token_id' in document:
            document['_id'] = document['token_id']
            del(document['token_id'])
        return document

    def _convertFromMongo(self, document):
        if document != None and '_id' in document:
            document['token_id'] = document['_id']
            del(document['_id'])
        return PasswordResetToken().dataImport(document)

    ### PUBLIC

    def addResetToken(self, token):
        logs.debug("Token: %s" % token.token_id)

        document = self._convertToMongo(token)
        document = self._addMongoDocument(document)
        token = self._convertFromMongo(document)

        return token

    def getResetToken(self, tokenId):
        document = self._getMongoDocumentFromId(tokenId)
        return self._convertFromMongo(document)
    
    def removeResetToken(self, tokenId):
        return self._removeMongoDocument(tokenId)

    def removeResetTokensForUser(self, userId):
        return self._collection.remove({'user_id': userId})

