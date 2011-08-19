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
        AMongoCollection.__init__(self, 'users')
        AAccountDB.__init__(self)
    
    def _convertToMongo(self, account):
        document = account.exportSparse()
        if 'user_id' in document:
            document['_id'] = self._getObjectIdFromString(document['user_id'])
            del(document['user_id'])
        if 'screen_name' in document:
            document['screen_name'] = str(document['screen_name']).lower()
        return document

    def _convertFromMongo(self, document):
        if '_id' in document:
            document['user_id'] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])
        return Account(document)
    
    ### PUBLIC
    
    def addAccount(self, user):
        ### TEMP: For now, verify that no duplicates can occur via index
        self._collection.ensure_index('screen_name', unique=True)

        document = self._convertToMongo(user)
        document = self._addMongoDocument(document)
        return self._convertFromMongo(document)
    
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

    def setProfileImageLink(self, userId, url):
        documentId = self._getObjectIdFromString(userId)
        self._collection.update(
            {'_id': documentId},
            {'$set': {'profile_image': url}}
            )
        return True
    
    def flagUser(self, user):
        # TODO
        raise NotImplementedError("TODO")

    def verifyAccountCredentials(self, screen_name, password):
        logs.debug("verifyAccountCredentials: %s:%s" % (screen_name, password))
        try:
            user = self._collection.find_one({'screen_name': screen_name})
            logs.debug("User data: %s" % (user))
            if auth.comparePasswordToStored(password, user['password']):
                return user['_id']
            return None
        except:
            return None

