#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import datetime, copy
import Globals, utils, logs

from errors import Fail

from AMongoCollection import AMongoCollection
from AAuthAccessTokenDB import AAuthAccessTokenDB

from AuthAccessToken import AuthAccessToken

class MongoAuthAccessTokenCollection(AMongoCollection, AAuthAccessTokenDB):
    
    SCHEMA = {
        '_id': basestring,
        'client_id': basestring,
        'refresh_token': basestring,
        'authenticated_user_id': basestring,
        'expires': datetime,
        'timestamp': {
            'created': datetime,
        },
    }
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='auth_accesstokens')
        AAuthAccessTokenDB.__init__(self)

    def addAccessToken(self, token):
        if token.isValid == False:
            logs.warning("Invalid token")
            raise KeyError("Token not valid")
        logs.debug("Token: %s" % token.token_id)
        # ret = self._addDocument(token, 'token_id')

        try:
            data = copy.copy(token.getDataAsDict())
            data['_id'] = data['token_id']
            del(data['token_id'])
            ### TODO: Get this to work.. not sure why it doesn't like me
            # obj = self._mapDataToSchema(data, self.SCHEMA)
            ret = self._collection.insert_one(data, safe=True)
            return ret
        except:
            raise Fail("%s | Unable to add token" % self) 

    def getAccessToken(self, tokenId):
        doc = self._collection.find_one(tokenId)
        logs.debug("Object retrieved")
        doc['token_id'] = doc['_id']
        del(doc['_id'])
        logs.debug("Id adjusted")

        token = AuthAccessToken(doc)
        logs.debug("Token converted")

        if token.isValid == False:
            logs.warning("Error: Token not valid")
            raise KeyError("Token not valid")

        return token

    def removeAccessToken(self, tokenId):
        return self._removeDocument(tokenId)
