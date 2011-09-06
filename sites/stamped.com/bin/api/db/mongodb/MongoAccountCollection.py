#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, auth, utils, logs
from datetime import datetime
from Schemas import *

from AMongoCollection import AMongoCollection
from AAccountDB import AAccountDB

class MongoAccountCollection(AMongoCollection, AAccountDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, 'users', primary_key='user_id', obj=Account)
        AAccountDB.__init__(self)
        
        ### TEMP: For now, verify that no duplicates can occur via index
        self._collection.ensure_index('screen_name_lower', unique=True)

    def _convertFromMongo(self, document):
        if 'screen_name_lower' in document:
            del(document['screen_name_lower'])
        
        return AMongoCollection._convertFromMongo(self, document)
    
    def _convertToMongo(self, account):
        document = AMongoCollection._convertToMongo(self, account)
        
        if 'screen_name' in document:
            document['screen_name_lower'] = str(document['screen_name']).lower()
        
        return document

    
    ### PUBLIC
    
    def addAccount(self, user):
        return self._addObject(user)
    
    def getAccount(self, userId):
        documentId = self._getObjectIdFromString(userId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)
    
    def updateAccount(self, user):
        document = self._convertToMongo(user)
        document = self._updateMongoDocument(document)
        return self._convertFromMongo(document)
    
    def removeAccount(self, userId):
        documentId = self._getObjectIdFromString(userId)
        return self._removeMongoDocument(documentId)
    
    def flagUser(self, user):
        # TODO
        raise NotImplementedError("TODO")

    def getAccountByEmail(self, email):
        email = str(email).lower()
        document = self._collection.find_one({"email": email})
        return self._convertFromMongo(document)
    
    def getAccountByScreenName(self, screenName):
        screenName = str(screenName).lower()
        document = self._collection.find_one({"screen_name_lower": screenName})
        return self._convertFromMongo(document)

