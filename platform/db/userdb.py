#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

import logs
from utils import lazyProperty

from db.mongodb.MongoUserCollection import MongoUserCollection

class UserDB(object):

    @lazyProperty
    def __user_collection(self):
        return MongoUserCollection()

    
    def getUser(self, userId):
        return self.__user_collection.getUser(userId)
    
    def getUserByScreenName(self, screenName):
        return self.__user_collection.getUserByScreenName(screenName)
    
    def checkScreenNameExists(self, screenName):
        return self.__user_collection.checkScreenNameExists(screenName)
    
    def lookupUsers(self, userIds=None, screenNames=None):
        return self.__user_collection.lookupUsers(userIds=userIds, screenNames=screenNames)
    
    def getUserMinis(self, userIds):
        return self.__user_collection.getUserMinis(userIds)
    
    def searchUsers(self, authUserId, query, limit=0, relationship=None):
        return self.__user_collection.searchUsers(authUserId, query, limit=limit, relationship=relationship)
    
    def updateUserStats(self, userIdOrIds, stat, value=None, increment=1):
        return self.__user_collection.updateUserStats(userIdOrIds, stat, value=value, increment=increment)

    def updateDistribution(self, userId, distribution):
        return self.__user_collection.updateDistribution(userId, distribution)
    
    def findUsersByEmail(self, emails, limit=0):
        return self.__user_collection.findUsersByEmail(emails, limit=limit)

    def findUsersByPhone(self, phone, limit=0):
        return self.__user_collection.findUsersByPhone(phone, limit=limit)

    def findUsersByTwitter(self, twitterIds, limit=0):
        return self.__user_collection.findUsersByTwitter(twitterIds, limit=limit)

    def findUsersByFacebook(self, facebookIds, limit=0):
        return self.__user_collection.findUsersByFacebook(facebookIds, limit=limit)

