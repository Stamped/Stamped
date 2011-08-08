#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import datetime, copy
import Globals, utils

from errors import Fail

from AMongoCollection import AMongoCollection
from AAuthRefreshTokenDB import AAuthRefreshTokenDB

from AuthRefreshToken import AuthRefreshToken

class MongoAuthRefreshTokenCollection(AMongoCollection, AAuthRefreshTokenDB):
    
    SCHEMA = {
        '_id': object,
        'client_id': basestring,
        'authenticated_user_id': basestring,
        'timestamp': {
            'created': datetime,
        },
        'access_tokens': list,
    }
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='auth_refreshtokens')
        AAuthRefreshTokenDB.__init__(self)
        

    def addRefreshToken(self, token):
        if token.isValid == False:
            raise KeyError("Token not valid")
        utils.log("Token: %s" % token.token_id)
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

    def getRefreshToken(self, tokenId, logPath=None):
        logPath = "%s | getRefreshToken" % logPath
        utils.logs.debug("%s | Begin" % logPath)

        doc = self._collection.find_one(tokenId)
        utils.logs.debug("%s | Object retrieved" % logPath)
        doc['token_id'] = doc['_id']
        del(doc['_id'])
        utils.logs.debug("%s | Id adjusted" % logPath)

        token = AuthRefreshToken(doc)
        utils.logs.debug("%s | Token converted" % logPath)

        if token.isValid == False:
            utils.logs.debug("%s | Error: Token not valid" % logPath)
            raise KeyError("Token not valid")

        utils.logs.debug("%s | Finish" % logPath)
        return token

    def removeRefreshToken(self, tokenId):
        return self._removeDocument(tokenId)
        
        
