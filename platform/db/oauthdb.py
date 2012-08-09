#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

import logs
from utils import lazyProperty

from db.mongodb.MongoAuthAccessTokenCollection import MongoAuthAccessTokenCollection
from db.mongodb.MongoAuthRefreshTokenCollection import MongoAuthRefreshTokenCollection

class OAuthDB(object):

    @lazyProperty
    def __access_token_collection(self):
        return MongoAuthAccessTokenCollection()

    @lazyProperty
    def __refresh_token_collection(self):
        return MongoAuthRefreshTokenCollection()
    
    ### REFRESH TOKEN

    def addRefreshToken(self, token):
        return self.__refresh_token_collection.addRefreshToken(token)

    def getRefreshToken(self, tokenId):
        return self.__refresh_token_collection.getRefreshToken(tokenId)
    
    def removeRefreshToken(self, tokenId):
        return self.__refresh_token_collection.removeRefreshToken(tokenId)

    def removeRefreshTokensForUser(self, userId):
        return self.__refresh_token_collection.removeRefreshTokensForUser(userId)

    ### ACCESS TOKEN

    def addAccessToken(self, token):
        return self.__access_token_collection.addAccessToken(token)

    def getAccessToken(self, tokenId):
        return self.__access_token_collection.getAccessToken(tokenId)
    
    def removeAccessToken(self, tokenId):
        return self.__access_token_collection.removeAccessToken(tokenId)

    def removeAccessTokensForUser(self, userId):
        return self.__access_token_collection.removeAccessTokensForUser(userId)
    

