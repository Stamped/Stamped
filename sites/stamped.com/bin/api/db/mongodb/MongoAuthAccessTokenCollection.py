#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import datetime, copy
import Globals, utils, logs

from errors import *
from Schemas import *

from AMongoCollection import AMongoCollection
from AAuthAccessTokenDB import AAuthAccessTokenDB

class MongoAuthAccessTokenCollection(AMongoCollection, AAuthAccessTokenDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='accesstokens', primary_key='token_id', obj=AccessToken)
        AAuthAccessTokenDB.__init__(self)
    
    ### PUBLIC
    
    def addAccessToken(self, token):
        logs.debug("Token: %s" % token.token_id)
        
        return self._addObject(token)
    
    def getAccessToken(self, tokenId):
        document = self._getMongoDocumentFromId(tokenId)
        return self._convertFromMongo(document)
    
    def removeAccessToken(self, tokenId):
        return self._removeMongoDocument(tokenId)

